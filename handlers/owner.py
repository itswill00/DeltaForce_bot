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

def is_owner(user_id: int) -> bool:
    return user_id == settings.owner_id

def get_admin_dashboard_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 CARI PERSONEL", callback_data="admin_search_user")
    builder.button(text="📋 AUDIT DATABASE", callback_data="admin_audit_db")
    builder.button(text="⚙️ SYSTEM INFO", callback_data="admin_sys_info")
    builder.button(text="◃ KEMBALI", callback_data="main_page_2")
    builder.adjust(1)
    return builder.as_markup()

@router.callback_query(F.data == "admin_dashboard")
async def admin_dashboard(callback: types.CallbackQuery, user_service: UserService):
    if not is_owner(callback.from_user.id):
        await callback.answer("Akses Ditolak.", show_alert=True)
        return
        
    stats = await user_service.get_global_stats()
    text = render_admin_dashboard(stats)
    
    await callback.message.edit_text(text, reply_markup=get_admin_dashboard_kb())
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
    text += f"<b>RAM Usage</b>: {ram.percent}%\n"
    text += f"<b>Uptime</b>: {uptime}s\n"
    text += f"<b>Total User</b>: {user_count}\n"
    text += f"<b>LFG Aktif</b>: {active_lfg_count}\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ KEMBALI", callback_data="admin_dashboard")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "admin_search_user")
async def admin_search_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id): return
    
    await callback.message.edit_text(
        get_header("Pencarian Personel", "🔍") +
        "Masukkan <b>IGN</b> atau <b>ID Telegram</b> user yang ingin dicari:",
        reply_markup=InlineKeyboardBuilder().button(text="◃ BATAL", callback_data="admin_dashboard").as_markup()
    )
    await state.set_state(AdminState.waiting_for_ign_search)
    await callback.answer()

@router.message(AdminState.waiting_for_ign_search)
async def process_admin_search(message: types.Message, state: FSMContext, user_service: UserService):
    if not is_owner(message.from_user.id): return
    
    query = message.text.strip()
    target_user = None
    
    if query.isdigit():
        target_user = await user_service.get_user(int(query))
    else:
        target_user = await user_service.find_user_by_ign(query)
        
    if not target_user:
        await message.answer("❌ Personel tidak ditemukan di database.")
        await state.clear()
        return
        
    text = render_admin_user_detail(target_user)
    
    builder = InlineKeyboardBuilder()
    # Management Actions
    builder.button(text="💎 TAMBAH 1K KOIN", callback_data=f"admin_mod_{target_user.id}_coin_1000")
    builder.button(text="🏅 TAMBAH 100 XP", callback_data=f"admin_mod_{target_user.id}_xp_100")
    builder.button(text="🗑️ RESET STATS", callback_data=f"admin_mod_{target_user.id}_reset")
    builder.button(text="◃ KEMBALI", callback_data="admin_dashboard")
    builder.adjust(2, 1, 1)
    
    await message.answer(text, reply_markup=builder.as_markup())
    await state.clear()

@router.callback_query(F.data.startswith("admin_mod_"))
async def process_admin_mod(callback: types.CallbackQuery, user_service: UserService):
    if not is_owner(callback.from_user.id): return
    
    parts = callback.data.split("_")
    target_id = int(parts[2])
    action = parts[3]
    
    if action == "coin":
        amount = int(parts[4])
        await user_service.add_balance(target_id, amount)
        await callback.answer(f"Berhasil menambah {amount} koin.")
    elif action == "xp":
        amount = int(parts[4])
        await user_service.add_xp(target_id, amount)
        await callback.answer(f"Berhasil menambah {amount} XP.")
    elif action == "reset":
        await user_service.update_user(target_id, {"xp": 0, "level": 1, "mabar_score": 0, "balance": 0})
        await callback.answer("Statistik user telah direset.", show_alert=True)

    # Refresh view
    user_data = await user_service.get_user(target_id)
    if user_data:
        await callback.message.edit_text(render_admin_user_detail(user_data), reply_markup=callback.message.reply_markup)

@router.callback_query(F.data == "admin_audit_db")
async def admin_audit_db(callback: types.CallbackQuery):
    if not is_owner(callback.from_user.id): return
    
    from aiogram.types import FSInputFile
    if os.path.exists(settings.local_db_path):
        await callback.message.answer_document(
            FSInputFile(settings.local_db_path),
            caption=f"◈ <b>AUDIT DATABASE</b>\nFile: <code>{settings.local_db_path}</code>\nStatus: Manual Request"
        )
        await callback.answer("File database dikirim.")
    else:
        await callback.answer("File tidak ditemukan.", show_alert=True)

@router.message(Command("sys"))
async def cmd_sys(message: types.Message, user_service: UserService, lfg_service: LfgService):
    if not is_owner(message.from_user.id): return
    # Reuse dashboard logic for simplicity
    await cmd_sys_logic(message, user_service, lfg_service)

async def cmd_sys_logic(message, user_service, lfg_service):
    user_count = await user_service.get_user_count()
    all_data = await lfg_service.db.get_all()
    active_lfg_count = len([k for k,v in all_data.get("lfg", {}).items() if v.get("status") == "open"])
    ram = psutil.virtual_memory()
    uptime = int(time.time() - psutil.boot_time())
    text = get_header("Sistem Kontrol Pusat", "⚙️")
    text += f"<b>RAM Usage</b>: {ram.percent}%\n<b>Uptime</b>: {uptime}s\n<b>Total User</b>: {user_count}\n<b>LFG Aktif</b>: {active_lfg_count}\n"
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ TUTUP", callback_data="close_msg")
    await message.answer(text, reply_markup=builder.as_markup())

@router.message(Command("refresh"))
async def cmd_refresh(message: types.Message):
    if not is_owner(message.from_user.id): return
    status_msg = await message.answer("◈ <b>Memulai Prosedur Update...</b>\n\n⬢ Menarik kode dari GitHub...")
    try:
        process = await asyncio.create_subprocess_shell("git pull origin main", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        output = stdout.decode().strip()
        if "Already up to date" in output:
            await status_msg.edit_text(get_header("Update Dibatalkan", "◈") + "Sistem sudah menggunakan versi terbaru di GitHub.\n\n" + f"<code>{output}</code>")
            return
        await status_msg.edit_text(get_header("Update Berhasil", "✅") + "Kode terbaru berhasil ditarik.\n\n" + f"<code>{output}</code>\n\n" + "<b>Sistem akan segera restart...</b>")
        await send_log(message.bot, "ADMIN_ACTION", f"Owner memicu /refresh. Sistem melakukan pull dan restart.")
        await asyncio.sleep(2)
        os.execv(sys.executable, [sys.executable, sys.argv[0], "--restart", str(message.chat.id), str(status_msg.message_id)])
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
