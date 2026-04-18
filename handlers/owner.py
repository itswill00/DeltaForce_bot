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
from utils.style_utils import get_header, get_footer, format_field, get_divider, force_height
from views.admin_view import render_admin_dashboard, render_admin_user_detail
from aiogram.utils.keyboard import InlineKeyboardBuilder
import psutil
import time
import os
import sys
import asyncio
import logging

router = Router()

class AdminState(StatesGroup):
    waiting_for_ign_search = State()
    waiting_for_value_set = State()
    waiting_for_mass_reward = State()
    waiting_for_blacklist_word = State()
    waiting_for_weapon_data = State()
    waiting_for_map_data = State()
    waiting_for_shop_data = State()
    waiting_for_banner_url = State()

def is_owner(user_id: int) -> bool:
    return int(user_id) == int(settings.owner_id)

async def safe_edit_media(callback: types.CallbackQuery, text: str, reply_markup):
    """Smartly edits a message whether it has a photo (caption) or is just text."""
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, reply_markup=reply_markup)
        else:
            await callback.message.edit_text(text=text, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Safe edit failed: {e}")
        # Fallback: send new message if edit fails
        await callback.message.answer(text=text, reply_markup=reply_markup)

def get_admin_dashboard_kb(maintenance_on: bool):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 CARI PERSONEL", callback_data="admin_search_user")
    builder.button(text="🎁 HADIAH MASSAL", callback_data="admin_mass_reward_prompt")
    builder.button(text="📂 INTEL CMS", callback_data="admin_intel_cms")
    builder.button(text="🖼️ VISUAL CMS", callback_data="admin_visual_cms")
    builder.button(text="🛡️ SECURITY HUB", callback_data="admin_security_hub")
    builder.button(text="🌐 SEKTOR GRUP", callback_data="admin_list_groups")
    builder.button(text="📋 AUDIT DATABASE", callback_data="admin_audit_db")
    m_text = "🔴 MATIKAN MAINTENANCE" if maintenance_on else "🟢 AKTIFKAN MAINTENANCE"
    builder.button(text=m_text, callback_data="admin_toggle_maint")
    builder.button(text="⚙️ SYSTEM INFO", callback_data="admin_sys_info")
    builder.button(text="◃ KEMBALI", callback_data="main_page_1")
    builder.adjust(2, 2, 2, 2, 2)
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
    
    await safe_edit_media(callback, text, get_admin_dashboard_kb(sys_settings.get('maintenance')))
    await callback.answer()

@router.callback_query(F.data == "admin_visual_cms")
async def admin_visual_cms(callback: types.CallbackQuery, system_service: SystemService):
    if not is_owner(callback.from_user.id): return
    text = get_header("Visual Management", "🖼️")
    text += "Kelola banner visual markas besar:\n\n"
    banners = ["main", "profile", "lfg", "shop", "intel"]
    builder = InlineKeyboardBuilder()
    for b in banners:
        builder.button(text=f"‣ BANNER {b.upper()}", callback_data=f"admin_banner_edit_{b}")
    builder.button(text="◃ KEMBALI", callback_data="admin_dashboard")
    builder.adjust(1)
    await safe_edit_media(callback, text, builder.as_markup())
    await callback.answer()

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
    await safe_edit_media(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "admin_cms_weapons")
async def admin_cms_weapons(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    weapons = await content_service.get_weapons()
    text = get_header("Manajemen Senjata", "🔫") + "Daftar arsenal aktif di database:\n\n"
    builder = InlineKeyboardBuilder()
    for wid, winfo in weapons.items():
        builder.button(text=f"‣ {winfo.get('name', wid)}", callback_data=f"admin_wpn_view_{wid}")
    builder.button(text="➕ TAMBAH SENJATA", callback_data="admin_wpn_add")
    builder.button(text="◃ KEMBALI", callback_data="admin_intel_cms")
    builder.adjust(2)
    await safe_edit_media(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "admin_cms_maps")
async def admin_cms_maps(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    maps = await content_service.get_maps()
    text = get_header("Manajemen Peta", "📍") + "Daftar sektor operasi aktif:\n\n"
    builder = InlineKeyboardBuilder()
    for mid, minfo in maps.items():
        builder.button(text=f"‣ {minfo.get('name', mid)}", callback_data=f"admin_map_view_{mid}")
    builder.button(text="➕ TAMBAH PETA", callback_data="admin_map_add")
    builder.button(text="◃ KEMBALI", callback_data="admin_intel_cms")
    builder.adjust(2)
    await safe_edit_media(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "admin_cms_shop")
async def admin_cms_shop(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    shop_items = await content_service.get_shop_items()
    text = get_header("Manajemen Bursa", "⌬") + "Katalog aktif di bursa komunitas:\n\n"
    builder = InlineKeyboardBuilder()
    for sid, sinfo in shop_items.items():
        builder.button(text=f"‣ {sinfo.get('name', sid)}", callback_data=f"admin_shop_view_{sid}")
    builder.button(text="➕ TAMBAH BARANG", callback_data="admin_shop_add")
    builder.button(text="◃ KEMBALI", callback_data="admin_intel_cms")
    builder.adjust(2)
    await safe_edit_media(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "admin_security_hub")
async def admin_security_hub(callback: types.CallbackQuery, security_service: SecurityService):
    if not is_owner(callback.from_user.id): return
    blacklist = await security_service.get_blacklist()
    text = get_header("Community Security", "🛡️") + "<b>GLOBAL BLACKLIST:</b>\n"
    text += "<code>" + ", ".join(blacklist) + "</code>" if blacklist else "<i>Belum ada kata terlarang.</i>"
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ TAMBAH KATA", callback_data="admin_bl_add")
    builder.button(text="🗑️ BERSIHKAN LIST", callback_data="admin_bl_clear")
    builder.button(text="◃ KEMBALI", callback_data="admin_dashboard")
    builder.adjust(2, 1)
    await safe_edit_media(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "admin_list_groups")
async def admin_list_groups(callback: types.CallbackQuery, group_service: GroupService):
    if not is_owner(callback.from_user.id): return
    data = await group_service.db.get_all()
    groups = data.get("groups", {})
    text = get_header("Audit Sektor Grup", "🌐")
    if not groups: text += "Belum ada grup yang terdaftar."
    else:
        for gid, ginfo in groups.items():
            text += f"‣ <b>{ginfo.get('title', 'Unknown')}</b>\n  ID: <code>{gid}</code>\n"
    builder = InlineKeyboardBuilder().button(text="◃ KEMBALI", callback_data="admin_dashboard")
    await safe_edit_media(callback, text, builder.as_markup())
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
    builder = InlineKeyboardBuilder().button(text="◃ KEMBALI", callback_data="admin_dashboard")
    await safe_edit_media(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_banner_edit_"))
async def admin_banner_edit_prompt(callback: types.CallbackQuery, state: FSMContext, system_service: SystemService):
    if not is_owner(callback.from_user.id): return
    key = callback.data.split("_")[3]
    current_url = await system_service.get_banner(key)
    await state.update_data(banner_key=key)
    text = get_header(f"Edit Banner: {key.upper()}", "🖼️") + f"<b>URL Saat Ini:</b>\n<code>{current_url}</code>\n\nKirimkan <b>Link Gambar (URL)</b> baru:"
    builder = InlineKeyboardBuilder().button(text="◃ BATAL", callback_data="admin_visual_cms")
    await safe_edit_media(callback, text, builder.as_markup())
    await state.set_state(AdminState.waiting_for_banner_url)
    await callback.answer()

@router.callback_query(F.data.startswith("admin_map_view_"))
async def admin_map_view(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    mid = callback.data.split("_")[3]
    maps = await content_service.get_maps()
    m = maps.get(mid)
    if not m:
        await callback.answer("Peta tidak ditemukan.", show_alert=True)
        return
    text = get_header(f"Sektor: {m['name']}", "📍") + f"<i>{m.get('description', '')}</i>\n\n<b>Hotspots:</b>\n" + "\n".join([f"‣ {h}" for h in m.get('hotspots', [])])
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑️ HAPUS", callback_data=f"admin_map_del_{mid}")
    builder.button(text="◃ KEMBALI", callback_data="admin_cms_maps")
    builder.adjust(1)
    await safe_edit_media(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("admin_wpn_view_"))
async def admin_weapon_view(callback: types.CallbackQuery, content_service: ContentService):
    if not is_owner(callback.from_user.id): return
    wid = callback.data.split("_")[3]
    weapons = await content_service.get_weapons()
    w = weapons.get(wid)
    if not w:
        await callback.answer("Senjata tidak ditemukan.", show_alert=True)
        return
    text = get_header(f"Arsenal: {w['name']}", "🔫") + format_field("TIER", w.get('tier', 'N/A')) + f"\n<b>Loadout:</b>\n<i>{w.get('best_loadout', 'TBA')}</i>"
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑️ HAPUS", callback_data=f"admin_wpn_del_{wid}")
    builder.button(text="◃ KEMBALI", callback_data="admin_cms_weapons")
    builder.adjust(1)
    await safe_edit_media(callback, text, builder.as_markup())
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
    text = get_header(f"Item: {item['name']}", "⌬") + format_field("HARGA", str(item.get('price', 0))) + format_field("TIPE", item.get('type', 'N/A')) + f"\n<i>\"{item.get('desc', 'N/A')}\"</i>\n"
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑️ HAPUS", callback_data=f"admin_shop_del_{sid}")
    builder.button(text="◃ KEMBALI", callback_data="admin_cms_shop")
    builder.adjust(1)
    await safe_edit_media(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "admin_cancel_state")
async def process_admin_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    # Go back to dashboard if state was cancelled
    await admin_dashboard(callback, UserService())

@router.callback_query(F.data == "admin_bl_clear")
async def admin_bl_clear(callback: types.CallbackQuery, security_service: SecurityService):
    if not is_owner(callback.from_user.id): return
    data = await security_service.db.get_all()
    data["system"]["blacklist"] = []
    await security_service.db.save(data)
    await callback.answer("Blacklist dibersihkan.", show_alert=True)
    await admin_security_hub(callback, security_service)

# --- REFRESH & SYS COMMANDS ---

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
    builder = InlineKeyboardBuilder().button(text="◃ TUTUP", callback_data="close_msg")
    await message.answer(text, reply_markup=builder.as_markup())

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

# --- PERSONNEL FSM ---

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
    text = get_header(f"Set {field.upper()}", "⚙️") + f"Masukkan nilai baru untuk ID <code>{target_id}</code>:"
    builder = InlineKeyboardBuilder().button(text="◃ BATAL", callback_data="admin_dashboard")
    await safe_edit_media(callback, text, builder.as_markup())
    await state.set_state(AdminState.waiting_for_value_set)
    await callback.answer()

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

# --- OTHER ADDERS ---
@router.message(AdminState.waiting_for_blacklist_word, ~F.text.startswith("/"))
async def process_bl_add(message: types.Message, state: FSMContext, security_service: SecurityService):
    if not is_owner(message.from_user.id): return
    word = message.text.strip().lower()
    await security_service.add_to_blacklist(word)
    await message.answer(f"✅ Kata <code>{word}</code> telah dimasukkan ke Blacklist Global.")
    await state.clear()

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

@router.message(AdminState.waiting_for_weapon_data, ~F.text.startswith("/"))
async def process_admin_wpn_add(message: types.Message, state: FSMContext, content_service: ContentService):
    if not is_owner(message.from_user.id): return
    try:
        import json
        w = json.loads(message.text)
        wid = w.pop("id", None)
        if not wid or not w.get("name"): raise ValueError("ID dan Nama wajib ada.")
        await content_service.update_weapon(wid, w)
        await message.answer(f"✅ Senjata <b>{w['name']}</b> berhasil ditambahkan.")
        await state.clear()
    except Exception as e: await message.answer(f"❌ <b>Format Salah:</b>\n<code>{str(e)}</code>")

@router.message(AdminState.waiting_for_map_data, ~F.text.startswith("/"))
async def process_admin_map_add(message: types.Message, state: FSMContext, content_service: ContentService):
    if not is_owner(message.from_user.id): return
    try:
        import json
        m = json.loads(message.text)
        mid = m.pop("id", None)
        if not mid or not m.get("name"): raise ValueError("ID dan Nama wajib ada.")
        await content_service.update_map(mid, m)
        await message.answer(f"✅ Peta <b>{m['name']}</b> berhasil ditambahkan.")
        await state.clear()
    except Exception as e: await message.answer(f"❌ <b>Format Salah:</b>\n<code>{str(e)}</code>")

@router.message(AdminState.waiting_for_shop_data, ~F.text.startswith("/"))
async def process_admin_shop_add(message: types.Message, state: FSMContext, content_service: ContentService):
    if not is_owner(message.from_user.id): return
    try:
        import json
        m = json.loads(message.text)
        mid = m.pop("id", None)
        if not mid or not m.get("name") or "price" not in m: raise ValueError("ID, Nama, dan Harga wajib ada.")
        await content_service.update_shop_item(mid, m)
        await message.answer(f"✅ Item <b>{m['name']}</b> berhasil ditambahkan.")
        await state.clear()
    except Exception as e: await message.answer(f"❌ <b>Format Salah:</b>\n<code>{str(e)}</code>")

@router.message(AdminState.waiting_for_banner_url, ~F.text.startswith("/"))
async def process_admin_banner_update(message: types.Message, state: FSMContext, system_service: SystemService):
    if not is_owner(message.from_user.id): return
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("❌ Format URL tidak valid.")
        return
    s_data = await state.get_data()
    key = s_data['banner_key']
    await system_service.set_banner(key, url)
    await message.answer(f"✅ Banner <b>{key.upper()}</b> berhasil diperbarui.")
    await state.clear()
