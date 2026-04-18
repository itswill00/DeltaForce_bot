from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import settings
from services.user_service import UserService
from services.lfg_service import LfgService
from utils.group_logger import send_log
from utils.style_utils import get_header, get_footer
from views.admin_view import render_admin_dashboard, render_admin_user_detail
from aiogram.utils.keyboard import InlineKeyboardBuilder
import psutil
import time
import os
import sys
import asyncio

router = Router()

class AdminState(StatesGroup):
    waiting_for_ign_search = State()
    waiting_for_value_set = State() # Generic state for setting XP/Level/Coin

def is_owner(user_id: int) -> bool:
    return int(user_id) == int(settings.owner_id)

def get_admin_dashboard_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 CARI PERSONEL", callback_data="admin_search_user")
    builder.button(text="📋 AUDIT DATABASE", callback_data="admin_audit_db")
    builder.button(text="⚙️ SYSTEM INFO", callback_data="admin_sys_info")
    builder.button(text="◃ KEMBALI", callback_data="main_page_2")
    builder.adjust(1)
    return builder.as_markup()

def get_personnel_mgmt_kb(target_id: int, is_admin: bool):
    builder = InlineKeyboardBuilder()
    # Row 1: Quick Buffs
    builder.button(text="💎 +1K COIN", callback_data=f"admin_mod_{target_id}_coin_1000")
    builder.button(text="🏅 +100 XP", callback_data=f"admin_mod_{target_id}_xp_100")
    # Row 2: Advanced Set
    builder.button(text="⚙️ SET LEVEL", callback_data=f"admin_set_{target_id}_level")
    builder.button(text="✨ SET XP", callback_data=f"admin_set_{target_id}_xp")
    # Row 3: Identity & Admin
    admin_btn = "❌ CABUT ADMIN" if is_admin else "🛡️ ANGKAT ADMIN"
    builder.button(text=admin_btn, callback_data=f"admin_mod_{target_id}_toggleadmin")
    # Row 4: Reset & Back
    builder.button(text="🗑️ RESET TOTAL", callback_data=f"admin_mod_{target_id}_reset")
    builder.button(text="◃ KEMBALI", callback_data="admin_dashboard")
    
    builder.adjust(2, 2, 1, 2)
    return builder.as_markup()

@router.callback_query(F.data == "admin_dashboard")
async def admin_dashboard(callback: types.CallbackQuery, user_service: UserService):
    if not is_owner(callback.from_user.id): return
    stats = await user_service.get_global_stats()
    await callback.message.edit_text(render_admin_dashboard(stats), reply_markup=get_admin_dashboard_kb())
    await callback.answer()

@router.callback_query(F.data == "admin_search_user")
async def admin_search_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id): return
    await callback.message.edit_text(
        get_header("Cari Personel", "🔍") + "Masukkan IGN atau ID Telegram:",
        reply_markup=InlineKeyboardBuilder().button(text="◃ BATAL", callback_data="admin_dashboard").as_markup()
    )
    await state.set_state(AdminState.waiting_for_ign_search)
    await callback.answer()

@router.message(AdminState.waiting_for_ign_search)
async def process_admin_search(message: types.Message, state: FSMContext, user_service: UserService):
    if not is_owner(message.from_user.id): return
    query = message.text.strip()
    target = await user_service.get_user(int(query)) if query.isdigit() else await user_service.find_user_by_ign(query)
    
    if not target:
        await message.answer("❌ Tidak ditemukan.")
        await state.clear()
        return
        
    await message.answer(render_admin_user_detail(target), reply_markup=get_personnel_mgmt_kb(target.id, target.is_admin))
    await state.clear()

@router.callback_query(F.data.startswith("admin_set_"))
async def admin_set_value_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id): return
    parts = callback.data.split("_")
    target_id, field = parts[2], parts[3]
    
    await state.update_data(target_id=target_id, field=field)
    await callback.message.answer(f"◈ <b>SET {field.upper()}</b>\nMasukkan nilai baru untuk ID <code>{target_id}</code>:")
    await state.set_state(AdminState.waiting_for_value_set)
    await callback.answer()

@router.message(AdminState.waiting_for_value_set)
async def process_admin_set_value(message: types.Message, state: FSMContext, user_service: UserService):
    if not is_owner(message.from_user.id): return
    val = message.text.strip()
    if not val.isdigit():
        await message.answer("❌ Masukkan angka saja.")
        return
        
    s_data = await state.get_data()
    target_id, field = int(s_data['target_id']), s_data['field']
    
    await user_service.update_user(target_id, {field: int(val)})
    await message.answer(f"✅ Berhasil mengubah <b>{field.upper()}</b> menjadi <code>{val}</code>.")
    
    # Show updated profile
    target = await user_service.get_user(target_id)
    await message.answer(render_admin_user_detail(target), reply_markup=get_personnel_mgmt_kb(target.id, target.is_admin))
    await state.clear()

@router.callback_query(F.data.startswith("admin_mod_"))
async def process_admin_mod(callback: types.CallbackQuery, user_service: UserService):
    if not is_owner(callback.from_user.id): return
    parts = callback.data.split("_")
    target_id, action = int(parts[2]), parts[3]
    
    if action == "coin":
        await user_service.add_balance(target_id, int(parts[4]))
    elif action == "xp":
        await user_service.add_xp(target_id, int(parts[4]))
    elif action == "toggleadmin":
        curr = await user_service.is_user_admin(target_id)
        await user_service.set_admin_status(target_id, not curr)
    elif action == "reset":
        await user_service.update_user(target_id, {"xp": 0, "level": 1, "balance": 0, "mabar_score": 0})
        
    target = await user_service.get_user(target_id)
    await callback.message.edit_text(render_admin_user_detail(target), reply_markup=get_personnel_mgmt_kb(target.id, target.is_admin))
    await callback.answer("Update Berhasil.")

@router.callback_query(F.data == "admin_audit_db")
async def admin_audit_db(callback: types.CallbackQuery):
    if not is_owner(callback.from_user.id): return
    from aiogram.types import FSInputFile
    if os.path.exists(settings.local_db_path):
        await callback.message.answer_document(FSInputFile(settings.local_db_path), caption="◈ <b>AUDIT DATABASE</b>")
    await callback.answer()

@router.callback_query(F.data == "admin_sys_info")
async def admin_sys_info(callback: types.CallbackQuery, user_service: UserService, lfg_service: LfgService):
    if not is_owner(callback.from_user.id): return
    user_count = await user_service.get_user_count()
    all_data = await lfg_service.db.get_all()
    active_lfg_count = len([k for k,v in all_data.get("lfg", {}).items() if v.get("status") == "open"])
    ram = psutil.virtual_memory()
    uptime = int(time.time() - psutil.boot_time())
    text = get_header("Sistem Kontrol Pusat", "⚙️")
    text += f"<b>RAM Usage</b>: {ram.percent}%\n<b>Uptime</b>: {uptime}s\n<b>Total User</b>: {user_count}\n<b>LFG Aktif</b>: {active_lfg_count}\n"
    await callback.message.edit_text(text, reply_markup=InlineKeyboardBuilder().button(text="◃ KEMBALI", callback_data="admin_dashboard").as_markup())
    await callback.answer()

@router.message(Command("sys"))
async def cmd_sys(message: types.Message, user_service: UserService, lfg_service: LfgService):
    if not is_owner(message.from_user.id): return
    user_count = await user_service.get_user_count()
    all_data = await lfg_service.db.get_all()
    active_lfg_count = len([k for k,v in all_data.get("lfg", {}).items() if v.get("status") == "open"])
    ram = psutil.virtual_memory()
    uptime = int(time.time() - psutil.boot_time())
    text = get_header("Sistem Kontrol Pusat", "⚙️")
    text += f"<b>RAM Usage</b>: {ram.percent}%\n<b>Uptime</b>: {uptime}s\n<b>Total User</b>: {user_count}\n<b>LFG Aktif</b>: {active_lfg_count}\n"
    await message.answer(text, reply_markup=InlineKeyboardBuilder().button(text="◃ TUTUP", callback_data="close_msg").as_markup())

@router.message(Command("refresh"))
async def cmd_refresh_prompt(message: types.Message):
    if not is_owner(message.from_user.id): return
    text = (get_header("Konfirmasi Update", "🔄") + "Sistem akan menarik kode terbaru dari GitHub dan melakukan restart otomatis.\n\n<b>Apakah Anda yakin ingin melanjutkan?</b>")
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ LANJUTKAN UPDATE", callback_data="admin_confirm_refresh")
    builder.button(text="◃ BATALKAN", callback_data="close_msg")
    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data == "admin_confirm_refresh")
async def process_refresh_execution(callback: types.CallbackQuery):
    if not is_owner(callback.from_user.id): return
    status_msg = callback.message
    await status_msg.edit_text("◈ <b>Memulai Prosedur Update...</b>\n\n⬢ Menarik kode dari GitHub...")
    try:
        process = await asyncio.create_subprocess_shell("git pull origin main", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
        stdout, _ = await process.communicate()
        output = stdout.decode().strip()
        if "Already up to date" in output or not output:
            await status_msg.edit_text(get_header("Sistem Terkini", "◈") + "Tidak ada pembaruan baru di GitHub.\n\n" + f"<pre>{output or 'Status: Up to date'}</pre>")
            return
        await status_msg.edit_text(get_header("Update Berhasil", "✅") + "<b>Log Pembaruan:</b>\n" + f"<pre>{output[:1000]}</pre>\n" + "<b>Sistem akan segera restart...</b>")
        await send_log(callback.bot, "ADMIN_ACTION", f"Owner mengonfirmasi /refresh. Sistem melakukan pull dan restart.")
        await asyncio.sleep(2)
        os.execv(sys.executable, [sys.executable, sys.argv[0], "--restart", str(callback.message.chat.id), str(status_msg.message_id)])
    except Exception as e:
        await status_msg.edit_text(f"❌ <b>Update Gagal:</b>\n<code>{str(e)}</code>")

@router.message(Command("addadmin"))
async def cmd_addadmin(message: types.Message, user_service: UserService):
    if not is_owner(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Format: <code>/addadmin ID_USER</code>")
        return
    target_id = int(args[1])
    await user_service.set_admin_status(target_id, True)
    await message.answer(f"Status Admin diberikan kepada ID <code>{target_id}</code>.")

@router.message(Command("deladmin"))
async def cmd_deladmin(message: types.Message, user_service: UserService):
    if not is_owner(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Format: <code>/deladmin ID_USER</code>")
        return
    target_id = int(args[1])
    await user_service.set_admin_status(target_id, False)
    await message.answer(f"Status Admin dicabut dari ID <code>{target_id}</code>.")

@router.message(Command("force_gc"))
async def cmd_force_gc(message: types.Message, lfg_service: LfgService):
    if not is_owner(message.from_user.id): return
    all_data = await lfg_service.db.get_all()
    all_sessions = all_data.get("lfg", {})
    to_delete = []
    current_time = time.time()
    for session_id, data in list(all_sessions.items()):
        ts = data.get("timestamp", 0)
        if ts and current_time - ts > 7200: to_delete.append(session_id)
    for s_id in to_delete:
        if s_id in all_data["lfg"]: del all_data["lfg"][s_id]
    await lfg_service.db.save(all_data)
    await message.answer(f"<b>PEMBERSIHAN</b>: {len(to_delete)} Sesi LFG dihapus.")
