from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import settings
from services.user_service import UserService
from services.lfg_service import LfgService
from services.system_service import SystemService
from services.group_service import GroupService
from services.content_service import ContentService
from services.security_service import SecurityService
from utils.group_logger import send_log
from utils.style_utils import get_header, get_footer, format_field, get_divider
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
    waiting_for_value_set = State()
    waiting_for_mass_reward = State()
    waiting_for_blacklist_word = State()
    # Content CMS States
    waiting_for_weapon_data = State()
    waiting_for_map_data = State()
    waiting_for_shop_data = State()

def is_owner(user_id: int) -> bool:
    return int(user_id) == int(settings.owner_id)

def get_admin_dashboard_kb(maintenance_on: bool):
    builder = InlineKeyboardBuilder()
    # Row 1: Users
    builder.button(text="🔍 CARI PERSONEL", callback_data="admin_search_user")
    builder.button(text="🎁 HADIAH MASSAL", callback_data="admin_mass_reward_prompt")
    # Row 2: Content & Security
    builder.button(text="📂 INTEL CMS", callback_data="admin_intel_cms")
    builder.button(text="🛡️ SECURITY HUB", callback_data="admin_security_hub")
    # Row 3: Groups & System
    builder.button(text="🌐 SEKTOR GRUP", callback_data="admin_list_groups")
    builder.button(text="📋 AUDIT DATABASE", callback_data="admin_audit_db")
    # Row 4: Maintenance Toggle
    m_text = "🔴 MATIKAN MAINTENANCE" if maintenance_on else "🟢 AKTIFKAN MAINTENANCE"
    builder.button(text=m_text, callback_data="admin_toggle_maint")
    # Row 5: Info & Exit
    builder.button(text="⚙️ SYSTEM INFO", callback_data="admin_sys_info")
    builder.button(text="◃ KEMBALI", callback_data="main_page_1")
    
    builder.adjust(2, 2, 2, 1, 2)
    return builder.as_markup()

@router.callback_query(F.data == "admin_dashboard")
async def admin_dashboard(callback: types.CallbackQuery, user_service: UserService):
    if not is_owner(callback.from_user.id): return
    sys_service = SystemService()
    sys_settings = await sys_service.get_settings()
    stats = await user_service.get_global_stats()
    
    text = render_admin_dashboard(stats)
    text += f"\n\n◈ <b>STATUS SISTEM:</b>\n"
    text += f"⬢ Maintenance: <code>{'AKTIF' if sys_settings.get('maintenance') else 'OFF'}</code>\n"
    text += f"⬢ Event Multiplier: <code>{sys_settings.get('event_multiplier', 1.0)}x</code>"
    
    await callback.message.edit_text(text, reply_markup=get_dashboard_kb_dynamic(sys_settings))
    await callback.answer()

def get_dashboard_kb_dynamic(sys_settings):
    return get_admin_dashboard_kb(sys_settings.get('maintenance'))

# --- INTEL CMS HANDLERS ---

@router.callback_query(F.data == "admin_intel_cms")
async def admin_intel_cms(callback: types.CallbackQuery):
    if not is_owner(callback.from_user.id): return
    text = get_header("Intelligence CMS", "📂")
    text += "Pusat kendali konten taktis. Silakan pilih kategori untuk diperbarui:"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🔫 MANAJEMEN SENJATA", callback_data="admin_cms_weapons")
    builder.button(text="📍 MANAJEMEN PETA", callback_data="admin_cms_maps")
    builder.button(text="⌬ MANAJEMEN BURSA", callback_data="admin_cms_shop")
    builder.button(text="◃ KEMBALI", callback_data="admin_dashboard")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "admin_cms_shop")
async def admin_cms_shop(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    shop_items = await content_service.get_shop_items()
    
    text = get_header("Manajemen Bursa", "⌬")
    text += "Katalog aktif di bursa komunitas:\n\n"
    
    builder = InlineKeyboardBuilder()
    for sid, sinfo in shop_items.items():
        builder.button(text=f"‣ {sinfo.get('name', sid)}", callback_data=f"admin_shop_view_{sid}")
    
    builder.button(text="➕ TAMBAH BARANG", callback_data="admin_shop_add")
    builder.button(text="◃ KEMBALI", callback_data="admin_intel_cms")
    builder.adjust(2)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_shop_view_"))
async def admin_shop_view(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    sid = callback.data.split("_")[3]
    shop_items = await content_service.get_shop_items()
    item = shop_items.get(sid)
    
    if not item:
        await callback.answer("Item tidak ditemukan.", show_alert=True)
        return
        
    text = get_header(f"Item: {item['name']}", "⌬")
    text += format_field("HARGA", str(item.get('price', 0)))
    text += format_field("TIPE", item.get('type', 'N/A'))
    text += f"\n<i>\"{item.get('desc', 'N/A')}\"</i>\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑️ HAPUS", callback_data=f"admin_shop_del_{sid}")
    builder.button(text="◃ KEMBALI", callback_data="admin_cms_shop")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_shop_del_"))
async def admin_shop_del(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    sid = callback.data.split("_")[3]
    await content_service.delete_shop_item(sid)
    await callback.answer("Item dihapus dari bursa.", show_alert=True)
    await admin_cms_shop(callback, content_service)

@router.callback_query(F.data == "admin_shop_add")
async def admin_shop_add_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id): return
    text = (
        get_header("Input Item Baru", "⌬") +
        "Kirimkan data item bursa dalam format JSON. Contoh:\n\n"
        "<code>{ \"id\": \"booster_xp\", \"name\": \"Double XP\", \"price\": 1000, \"type\": \"booster\", \"desc\": \"XP 2x lipat!\" }</code>"
    )
    builder = InlineKeyboardBuilder().button(text="◃ BATAL", callback_data="admin_cancel_state")
    await callback.message.answer(text, reply_markup=builder.as_markup())
    await state.set_state(AdminState.waiting_for_shop_data)
    await callback.answer()

@router.message(AdminState.waiting_for_shop_data, ~F.text.startswith("/"))
async def process_admin_shop_add(message: types.Message, state: FSMContext, content_service: ContentService):
    if not is_owner(message.from_user.id): return
    try:
        import json
        m = json.loads(message.text)
        mid = m.pop("id", None)
        if not mid or not m.get("name") or "price" not in m: raise ValueError("ID, Nama, dan Harga wajib ada.")
        
        await content_service.update_shop_item(mid, m)
        await message.answer(f"✅ Item <b>{m['name']}</b> berhasil ditambahkan ke bursa.")
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ <b>Format Salah:</b>\n<code>{str(e)}</code>")

@router.callback_query(F.data == "admin_cms_maps")
async def admin_cms_maps(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    maps = await content_service.get_maps()
    
    text = get_header("Manajemen Peta", "📍")
    text += "Daftar sektor operasi aktif:\n\n"
    
    builder = InlineKeyboardBuilder()
    for mid, minfo in maps.items():
        builder.button(text=f"‣ {minfo.get('name', mid)}", callback_data=f"admin_map_view_{mid}")
    
    builder.button(text="➕ TAMBAH PETA", callback_data="admin_map_add")
    builder.button(text="◃ KEMBALI", callback_data="admin_intel_cms")
    builder.adjust(2)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "admin_wpn_add")
async def admin_wpn_add_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id): return
    text = (
        get_header("Input Arsenal Baru", "🔫") +
        "Kirimkan data senjata dalam format JSON. Contoh:\n\n"
        "<code>{ \"id\": \"m416\", \"name\": \"M416\", \"tier\": \"S\", \"category\": \"Assault\", \"best_loadout\": \"...\" }</code>"
    )
    builder = InlineKeyboardBuilder().button(text="◃ BATAL", callback_data="admin_cancel_state")
    await callback.message.answer(text, reply_markup=builder.as_markup())
    await state.set_state(AdminState.waiting_for_weapon_data)
    await callback.answer()

@router.message(AdminState.waiting_for_weapon_data, ~F.text.startswith("/"))
async def process_admin_wpn_add(message: types.Message, state: FSMContext, content_service: ContentService):
    if not is_owner(message.from_user.id): return
    try:
        import json
        w = json.loads(message.text)
        wid = w.pop("id", None)
        if not wid or not w.get("name"): raise ValueError("ID dan Nama wajib ada.")
        
        await content_service.update_weapon(wid, w)
        await message.answer(f"✅ Senjata <b>{w['name']}</b> berhasil ditambahkan ke database.")
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ <b>Format Salah:</b>\n<code>{str(e)}</code>")

@router.callback_query(F.data == "admin_map_add")
async def admin_map_add_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id): return
    text = (
        get_header("Input Sektor Baru", "📍") +
        "Kirimkan data peta dalam format JSON. Contoh:\n\n"
        "<code>{ \"id\": \"dam\", \"name\": \"Dam\", \"description\": \"...\", \"hotspots\": [\"A\", \"B\"] }</code>"
    )
    builder = InlineKeyboardBuilder().button(text="◃ BATAL", callback_data="admin_cancel_state")
    await callback.message.answer(text, reply_markup=builder.as_markup())
    await state.set_state(AdminState.waiting_for_map_data)
    await callback.answer()

@router.message(AdminState.waiting_for_map_data, ~F.text.startswith("/"))
async def process_admin_map_add(message: types.Message, state: FSMContext, content_service: ContentService):
    if not is_owner(message.from_user.id): return
    try:
        import json
        m = json.loads(message.text)
        mid = m.pop("id", None)
        if not mid or not m.get("name"): raise ValueError("ID dan Nama wajib ada.")
        
        await content_service.update_map(mid, m)
        await message.answer(f"✅ Peta <b>{m['name']}</b> berhasil ditambahkan ke database.")
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ <b>Format Salah:</b>\n<code>{str(e)}</code>")

@router.callback_query(F.data.startswith("admin_map_view_"))
async def admin_map_view(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    mid = callback.data.split("_")[3]
    maps = await content_service.get_maps()
    m = maps.get(mid)
    
    if not m:
        await callback.answer("Peta tidak ditemukan.", show_alert=True)
        return
        
    text = get_header(f"Sektor: {m['name']}", "📍")
    text += f"<i>{m.get('description', '')}</i>\n\n"
    text += "<b>Hotspots:</b>\n" + "\n".join([f"‣ {h}" for h in m.get('hotspots', [])])
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑️ HAPUS", callback_data=f"admin_map_del_{mid}")
    builder.button(text="◃ KEMBALI", callback_data="admin_cms_maps")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_map_del_"))
async def admin_map_del(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    mid = callback.data.split("_")[3]
    
    data = await content_service.db.get_all()
    if mid in data["content"]["maps"]:
        del data["content"]["maps"][mid]
        await content_service.db.save(data)
        
    await callback.answer("Peta dihapus.", show_alert=True)
    await admin_cms_maps(callback, content_service)

@router.callback_query(F.data.startswith("admin_wpn_view_"))
async def admin_weapon_view(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    wid = callback.data.split("_")[3]
    weapons = await content_service.get_weapons()
    w = weapons.get(wid)
    
    if not w:
        await callback.answer("Senjata tidak ditemukan.", show_alert=True)
        return
        
    text = get_header(f"Arsenal: {w['name']}", "🔫")
    text += format_field("TIER", w.get('tier', 'N/A'))
    text += f"\n<b>Loadout:</b>\n<i>{w.get('best_loadout', 'TBA')}</i>"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑️ HAPUS", callback_data=f"admin_wpn_del_{wid}")
    builder.button(text="◃ KEMBALI", callback_data="admin_cms_weapons")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_wpn_del_"))
async def admin_weapon_del(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    wid = callback.data.split("_")[3]
    await content_service.delete_weapon(wid)
    await callback.answer("Senjata dihapus.", show_alert=True)
    await admin_cms_weapons(callback, content_service)

# --- SECURITY HUB HANDLERS ---

@router.callback_query(F.data == "admin_security_hub")
async def admin_security_hub(callback: types.CallbackQuery, security_service: SecurityService):
    if not is_owner(callback.from_user.id): return
    blacklist = await security_service.get_blacklist()
    
    text = get_header("Community Security", "🛡️")
    text += "<b>GLOBAL BLACKLIST:</b>\n"
    if not blacklist:
        text += "<i>Belum ada kata terlarang.</i>"
    else:
        text += "<code>" + ", ".join(blacklist) + "</code>"
        
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ TAMBAH KATA", callback_data="admin_bl_add")
    builder.button(text="🗑️ BERSIHKAN LIST", callback_data="admin_bl_clear")
    builder.button(text="◃ KEMBALI", callback_data="admin_dashboard")
    builder.adjust(2, 1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "admin_bl_add")
async def admin_bl_add_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id): return
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ BATAL", callback_data="admin_cancel_state")
    await callback.message.answer(
        "◈ <b>SECURITY PROTOCOL</b>\nMasukkan kata/frasa yang ingin dilarang secara global:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(AdminState.waiting_for_blacklist_word)
    await callback.answer()

@router.message(AdminState.waiting_for_blacklist_word, ~F.text.startswith("/"))
async def process_bl_add(message: types.Message, state: FSMContext, security_service: SecurityService):
    if not is_owner(message.from_user.id): return
    word = message.text.strip().lower()
    await security_service.add_to_blacklist(word)
    await message.answer(f"✅ Kata <code>{word}</code> telah dimasukkan ke Blacklist Global.")
    await state.clear()

# --- CORE SYSTEM HANDLERS ---

@router.callback_query(F.data == "admin_toggle_maint")
async def admin_toggle_maint(callback: types.CallbackQuery):
    if not is_owner(callback.from_user.id): return
    sys_service = SystemService()
    new_status = await sys_service.toggle_maintenance()
    await callback.answer(f"Maintenance Mode: {'AKTIF' if new_status else 'OFF'}", show_alert=True)
    await admin_dashboard(callback, UserService())

@router.callback_query(F.data == "admin_audit_db")
async def admin_audit_db(callback: types.CallbackQuery):
    if not is_owner(callback.from_user.id): return
    from aiogram.types import FSInputFile
    if os.path.exists(settings.local_db_path):
        await callback.message.answer_document(FSInputFile(settings.local_db_path), caption="◈ <b>AUDIT DATABASE</b>")
    await callback.answer()

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

# Personnel Management functions from previous Turn (Search, Mod, Set)
# I will integrate them here to ensure everything is in one mature file.

@router.callback_query(F.data == "admin_mass_reward_prompt")
async def admin_reward_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id): return
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ BATAL", callback_data="admin_cancel_state")
    await callback.message.edit_text(
        get_header("Suntikan Dana Massal", "🎁") + 
        "Masukkan jumlah <b>KOIN</b> yang akan dibagikan ke SELURUH user terdaftar:", 
        reply_markup=builder.as_markup()
    )
    await state.set_state(AdminState.waiting_for_mass_reward)
    await callback.answer()

@router.message(AdminState.waiting_for_mass_reward, ~F.text.startswith("/"))
async def process_mass_reward(message: types.Message, state: FSMContext):
    if not is_owner(message.from_user.id): return
    val = message.text.strip()
    if not val.isdigit():
        await message.answer("❌ Masukkan angka saja.")
        return
    sys_service = SystemService()
    count = await sys_service.mass_reward(coin_amount=int(val))
    await message.answer(f"✅ <b>MISI BERHASIL</b>\n\nSebanyak <code>{val}</code> Koin telah disuntikkan ke <code>{count}</code> operator terdaftar.")
    await state.clear()

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

def get_personnel_mgmt_kb(target_id: int, is_admin: bool):
    builder = InlineKeyboardBuilder()
    builder.button(text="💎 +1K COIN", callback_data=f"admin_mod_{target_id}_coin_1000")
    builder.button(text="🏅 +100 XP", callback_data=f"admin_mod_{target_id}_xp_100")
    builder.button(text="⚙️ SET LEVEL", callback_data=f"admin_set_{target_id}_level")
    builder.button(text="✨ SET XP", callback_data=f"admin_set_{target_id}_xp")
    admin_btn = "❌ CABUT ADMIN" if is_admin else "🛡️ ANGKAT ADMIN"
    builder.button(text=admin_btn, callback_data=f"admin_mod_{target_id}_toggleadmin")
    builder.button(text="🗑️ RESET TOTAL", callback_data=f"admin_mod_{target_id}_reset")
    builder.button(text="◃ KEMBALI", callback_data="admin_dashboard")
    builder.adjust(2, 2, 1, 2)
    return builder.as_markup()

@router.callback_query(F.data.startswith("admin_mod_"))
async def process_admin_mod(callback: types.CallbackQuery, user_service: UserService):
    if not is_owner(callback.from_user.id): return
    parts = callback.data.split("_")
    target_id, action = int(parts[2]), parts[3]
    if action == "coin": await user_service.add_balance(target_id, int(parts[4]))
    elif action == "xp": await user_service.add_xp(target_id, int(parts[4]))
    elif action == "toggleadmin":
        curr = await user_service.is_user_admin(target_id)
        await user_service.set_admin_status(target_id, not curr)
    elif action == "reset": await user_service.update_user(target_id, {"xp": 0, "level": 1, "balance": 0, "mabar_score": 0})
    target = await user_service.get_user(target_id)
    await callback.message.edit_text(render_admin_user_detail(target), reply_markup=get_personnel_mgmt_kb(target.id, target.is_admin))
    await callback.answer("Update Berhasil.")

@router.callback_query(F.data.startswith("admin_set_"))
async def admin_set_value_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not is_owner(callback.from_user.id): return
    parts = callback.data.split("_")
    target_id, field = parts[2], parts[3]
    
    await state.update_data(target_id=target_id, field=field)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ BATAL", callback_data="admin_cancel_state")
    
    await callback.message.answer(
        f"◈ <b>SET {field.upper()}</b>\nMasukkan nilai baru untuk ID <code>{target_id}</code>:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(AdminState.waiting_for_value_set)
    await callback.answer()

@router.callback_query(F.data == "admin_cancel_state")
async def process_admin_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.answer("Aksi dibatalkan.")

@router.message(AdminState.waiting_for_value_set, ~F.text.startswith("/"))
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
    target = await user_service.get_user(target_id)
    if target:
        await message.answer(render_admin_user_detail(target), reply_markup=get_personnel_mgmt_kb(target.id, target.is_admin))
    await state.clear()
