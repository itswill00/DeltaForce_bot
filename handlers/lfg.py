from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.user_db import user_db
from utils.style_utils import get_header, get_footer
import uuid
import asyncio
from utils.auto_delete import set_auto_delete

router = Router()

@router.message(Command("mabar"))
@router.callback_query(F.data == "main_mabar")
async def cmd_mabar(event: types.Message | types.CallbackQuery):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    
    # Track group if in group
    if message.chat.type != "private":
        from database.group_db import group_db
        await group_db.register_group(message.chat.id, message.chat.title)
        await group_db.track_member(message.chat.id, event.from_user.id)
    
    # Check registration
    user_info = await user_db.get_user(event.from_user.id)
    if not user_info or "ign" not in user_info:
        text = "❌ AKSES DITOLAK: Anda harus /register profil sebelum bisa membuka lobi mabar."
        builder = InlineKeyboardBuilder()
        builder.button(text="🚀 Daftar Sekarang", callback_data="start_register")
        builder.button(text="🏠 Menu Utama", callback_data="main_menu")
        
        if is_callback:
            await event.message.edit_text(text, reply_markup=builder.as_markup())
        else:
            await message.answer(text, reply_markup=builder.as_markup())
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 Hazard Ops (3-Pemain)", callback_data="lfghost_hazard")
    builder.button(text="⚔️ Havoc Warfare (4-Pemain)", callback_data="lfghost_havoc")
    builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    builder.adjust(1)
    
    text = get_header("PENGATURAN MABAR", "🕹️")
    text += "Pilih mode operasi untuk lobi mabar Anda:"
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=builder.as_markup())
        await event.answer()
    else:
        await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("lfghost_"))
async def process_lfg_host(callback: types.CallbackQuery):
    lfg_type = callback.data.split("_")[1]
    
    user_info = await user_db.get_user(callback.from_user.id)
    host_name = user_info.get("first_name", callback.from_user.first_name) if user_info else callback.from_user.first_name
    
    session_id = str(uuid.uuid4())[:8]
    host_id = callback.from_user.id
    
    max_p = 3 if lfg_type == "hazard" else 4
    
    session_data = {
        "host_id": host_id,
        "host_name": host_name,
        "players": [host_id],
        "max_players": max_p,
        "status": "open",
        "lfg_type": lfg_type,
        "timestamp": __import__('time').time()
    }
    
    await lfg_db.update_session(session_id, session_data)
    
    from utils.group_logger import send_log
    tipe_str = "Hazard Operation" if lfg_type == "hazard" else "Havoc Warfare"
    await send_log(
        callback.bot,
        "LFG_CREATED",
        f"<b>{host_name}</b> membuka LFG baru!\nMode: {tipe_str}"
    )
    
    text, markup = await build_lfg_message(session_id, session_data)
    # Delete the setup message and send the main LFG interface
    try:
        await callback.message.delete()
    except:
        pass
    
    lfg_msg = await callback.message.answer(text, reply_markup=markup)
    await callback.answer("Penugasan disetujui.")
    
    # Auto-cleanup for host message if in group
    if callback.message.chat.type != "private":
        from database.group_db import group_db
        group_info = await group_db.get_group(callback.message.chat.id)
        if group_info and group_info.get("settings", {}).get("auto_cleanup", True):
            asyncio.create_task(set_auto_delete(lfg_msg, None, 600)) # 10 minutes timeout

async def build_lfg_message(session_id: str, session_data: dict):
    player_count = len(session_data["players"])
    max_p = session_data["max_players"]
    status_text = "🟢 ACTIVE" if session_data["status"] == "open" else "🔴 DEPLOYED/CLOSED"
    
    lfg_type = session_data.get("lfg_type", "hazard")
    tipe_str = "HAZARD OPERATION" if lfg_type == "hazard" else "HAVOC WARFARE"
    icon = "☣️" if lfg_type == "hazard" else "⚔️"
    
    text = get_header(f"DEPLOYMENT ORDER #{session_id.upper()}", icon)
    text += (
        f"<b>OPERASI:</b> {tipe_str}\n"
        f"<b>STATUS:</b> {status_text}\n"
        f"<b>KUOTA:</b> {player_count}/{max_p} OPERATOR\n"
        f"─" * 15 + "\n"
        f"<b>MANIFES SKUAD:</b>\n"
    )
    
    for i, pid in enumerate(session_data["players"]):
        user_info = await user_db.get_user(pid)
        is_host = " [LEADER]" if pid == session_data["host_id"] else ""
        if user_info:
            ign = user_info.get('ign', 'Unknown')
            role = user_info.get('role', 'N/A')
            text += f"{i+1}. <b>{ign}</b> ({role}){is_host}\n"
        else:
            text += f"{i+1}. Operator-ID:{pid}{is_host}\n"
            
    for i in range(player_count, max_p):
        text += f"{i+1}. [ 🔓 SLOT TERSEDIA ]\n"
    
    text += f"─" * 15 + "\n"
    if session_data["status"] == "open":
        text += "<i>Menunggu otorisasi skuad penuh untuk pendeploian...</i>"
    else:
        text += "<i>Unit telah dideploy ke area operasi.</i>"

    builder = InlineKeyboardBuilder()
    
    if session_data["status"] == "open":
        builder.button(text="➕ Gabung", callback_data=f"lfg_join_{session_id}")
        builder.button(text="➖ Keluar", callback_data=f"lfg_leave_{session_id}")
        builder.button(text="🔊 Ping", callback_data=f"lfg_ping_{session_id}")
        
        if callback.message.chat.type == "private":
            builder.button(text="🏠 Menu", callback_data="main_menu")
        else:
            bot_user = await callback.bot.get_me()
            builder.button(text="👤 Profil (DM)", url=f"https://t.me/{bot_user.username}?start=profile")
    else:
        if callback.message.chat.type == "private":
            builder.button(text="🏠 Menu Utama", callback_data="main_menu")
        else:
            bot_user = await callback.bot.get_me()
            builder.button(text="👤 Profil (DM)", url=f"https://t.me/{bot_user.username}?start=profile")
        
    builder.adjust(2)
    return text, builder.as_markup()

@router.callback_query(F.data.startswith("lfg_"))
async def process_lfg(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    if action == "noop":
        await callback.answer("Sesi ini sudah ditutup/penuh.", show_alert=True)
        return
        
    session_id = callback.data.split("_")[2]
    user_id = callback.from_user.id
    
    session_data = await lfg_db.get_session(session_id)
    if not session_data:
        await callback.answer("Sesi mabar tidak ditemukan atau sudah kadaluarsa.", show_alert=True)
        return
        
    # Join logic
    if action == "join":
        # Check if user is registered first
        user_info = await user_db.get_user(user_id)
        if not user_info or "ign" not in user_info:
            await callback.answer("❌ AKSES DITOLAK: Hubungkan Profil ( /register ) Anda sebelum bergabung dalam operasi.", show_alert=True)
            return

        if user_id in session_data["players"]:
            await callback.answer("⚠️ Anda sudah terdaftar dalam manifes skuad ini.")
        elif len(session_data["players"]) >= session_data["max_players"]:
            await callback.answer("⚠️ KAPASITAS MAKSIMUM: Skuad telah mencapai batas personel.")
        else:
            session_data["players"].append(user_id)
            
            # Track group member
            if callback.message.chat.type != "private":
                from database.group_db import group_db
                await group_db.track_member(callback.message.chat.id, user_id)
            
            # If squad becomes full, auto-close and award points
            if len(session_data["players"]) == session_data["max_players"]:
                session_data["status"] = "closed"
                await lfg_db.update_session(session_id, session_data)
                text, markup = await build_lfg_message(session_id, session_data)
                
                # Award points to all players
                for p_id in session_data["players"]:
                    await user_db.increment_mabar_score(p_id)
                    
                from utils.group_logger import send_log
                await send_log(
                    callback.bot,
                    "LFG_FULL",
                    f"Skuad LFG (Host: {session_data['host_name']}) telah mencapai kapasitas maksimum (4/4)."
                )
                    
                await callback.message.edit_text(text, reply_markup=markup)
                conf_msg = await callback.message.answer(
                    f"✅ <b>KONFIRMASI PENUGASAN</b>\n"
                    f"Skuad <b>{session_data['host_name']}</b> telah siap tempur.\n"
                    f"Bonus +25 XP dan +1 Skor Mabar diberikan seluruh personel."
                )
                await callback.answer("Penugasan divalidasi. Skuad penuh.")
                
                # Auto-cleanup confirmation after 60 seconds
                if callback.message.chat.type != "private":
                    from database.group_db import group_db
                    group_info = await group_db.get_group(callback.message.chat.id)
                    if group_info and group_info.get("settings", {}).get("auto_cleanup", True):
                        asyncio.create_task(set_auto_delete(conf_msg, None, 60))
                return
            
            await lfg_db.update_session(session_id, session_data)
            text, markup = await build_lfg_message(session_id, session_data)
            await callback.message.edit_text(text, reply_markup=markup)
            await callback.answer("Bergabung ke skuad.")
            
    # Leave logic
    elif action == "leave":
        if user_id in session_data["players"]:
            if user_id == session_data["host_id"]:
                session_data["status"] = "closed"
                await lfg_db.update_session(session_id, session_data)
                text = f"<b>LFG DIBATALKAN</b>\nHost telah membatalkan sesi ini."
                await callback.message.edit_text(text)
                await callback.answer("LFG Dibatalkan.")
            else:
                session_data["players"].remove(user_id)
                await lfg_db.update_session(session_id, session_data)
                
                text, markup = await build_lfg_message(session_id, session_data)
                await callback.message.edit_text(text, reply_markup=markup)
                await callback.answer("Keluar dari skuad.")
        else:
            await callback.answer("Anda tidak berada di dalam skuad ini.")
            
    # Close logic
    elif action == "close":
        if user_id == session_data["host_id"]:
            session_data["status"] = "closed"
            await lfg_db.update_session(session_id, session_data)
            text, markup = await build_lfg_message(session_id, session_data)
            await callback.message.edit_text(text, reply_markup=markup)
            await callback.answer("Sesi dialihkan ke mode tertutup.")
        else:
            await callback.answer("Penolakan akses: Hanya Host yang dapat menutup sesi.", show_alert=True)

    # Ping logic
    elif action == "ping":
        if user_id == session_data["host_id"] or user_id in session_data["players"]:
            current_roles = []
            for p_id in session_data["players"]:
                u = await user_db.get_user(p_id)
                if u and "role" in u:
                    current_roles.append(u["role"])
                    
            lfg_type = session_data.get("lfg_type", "hazard")
            ping_text = f"<b>PEMBERITAHUAN SKUAD:</b>\nSkuad <b>{session_data['host_name']}</b> membutuhkan tambahan personel."
            
            if lfg_type == "hazard":
                ping_text += f"\n<b>Mode:</b> Hazard Operation (Ekstraksi/Loot)\n<b>Kekurangan:</b> {session_data['max_players'] - len(session_data['players'])} Operator (Prioritas Medis/Recon)."
            else:
                ping_text += f"\n<b>Mode:</b> Havoc Warfare (Skala Besar/Objektif)\n<b>Kekurangan:</b> {session_data['max_players'] - len(session_data['players'])} Operator (Prioritas Tempur)."
                
            ping_text += "\n\n<i>Ketuk [Gabung] di antarmuka LFG utama.</i>"
            
            await callback.message.reply(ping_text)
            await callback.answer("Notifikasi dikirim.")
        else:
            await callback.answer("Aksi ditolak. Bergabunglah terlebih dahulu.", show_alert=True)
