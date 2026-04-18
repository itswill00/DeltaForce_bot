from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import UserService
from services.lfg_service import LfgService
from utils.style_utils import get_header, get_footer
from utils.auto_delete import set_auto_delete
from views.lfg_view import render_lfg
import asyncio

router = Router()

@router.message(Command("mabar"))
@router.callback_query(F.data == "main_mabar")
async def cmd_mabar(event: types.Message | types.CallbackQuery, user_service: UserService):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    
    # Check registration
    user_info = await user_service.get_user(event.from_user.id)
    if not user_info or not user_info.ign:
        text = "❌ <b>AKSES DITOLAK:</b> Anda harus <code>/register</code> profil sebelum bisa membuka lobi mabar."
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
async def process_lfg_host(callback: types.CallbackQuery, user_service: UserService, lfg_service: LfgService):
    lfg_type = callback.data.split("_")[1]
    user_info = await user_service.get_user(callback.from_user.id)
    host_name = user_info.ign if user_info else callback.from_user.first_name
    
    max_p = 3 if lfg_type == "hazard" else 4
    session = await lfg_service.create_session(callback.from_user.id, host_name, lfg_type, max_p)
    
    from utils.group_logger import send_log
    tipe_str = "Hazard Operation" if lfg_type == "hazard" else "Havoc Warfare"
    await send_log(
        callback.bot,
        "LFG_CREATED",
        f"<b>{host_name}</b> membuka LFG baru!\nMode: {tipe_str}"
    )
    
    text, markup = await build_lfg_interface(session, user_service, callback.bot)
    try:
        await callback.message.delete()
    except:
        pass
    
    lfg_msg = await callback.message.answer(text, reply_markup=markup)
    await callback.answer("Penugasan disetujui.")
    
    if callback.message.chat.type != "private":
        asyncio.create_task(set_auto_delete(lfg_msg, None, 600))

async def build_lfg_interface(session, user_service: UserService, bot):
    # Resolve player names and roles for the view
    player_data = []
    for pid in session.players:
        u = await user_service.get_user(pid)
        if u:
            player_data.append(f"<b>{u.ign}</b> (<code>{u.role}</code>)")
        else:
            player_data.append(f"Operator-ID:<code>{pid}</code>")
            
    # Use the View Layer
    text = render_lfg(session, player_data)

    builder = InlineKeyboardBuilder()
    if session.status == "open":
        builder.button(text="➕ Gabung", callback_data=f"lfg_join_{session.id}")
        builder.button(text="➖ Keluar", callback_data=f"lfg_leave_{session.id}")
        builder.button(text="🔊 Ping", callback_data=f"lfg_ping_{session.id}")
    
    bot_user = await bot.get_me()
    builder.button(text="👤 Profil (DM)", url=f"https://t.me/{bot_user.username}?start=profile")
    builder.adjust(2)
    
    return text, builder.as_markup()

@router.callback_query(F.data.startswith("lfg_"))
async def process_lfg_action(callback: types.CallbackQuery, user_service: UserService, lfg_service: LfgService):
    parts = callback.data.split("_")
    action = parts[1]
    session_id = parts[2]
    
    if action == "join":
        session, msg = await lfg_service.join_session(session_id, callback.from_user.id)
        if not session:
            await callback.answer(f"⚠️ {msg}", show_alert=True)
            return
            
        text, markup = await build_lfg_interface(session, user_service, callback.bot)
        await callback.message.edit_text(text, reply_markup=markup)
        await callback.answer(msg)
        
        if session.status == "closed":
            conf_msg = await callback.message.answer(
                f"✅ <b>SKUAD SIAP TEMPUR</b>\n"
                f"Skuad <b>{session.host_name}</b> telah siap.\n"
                f"Bonus +25 XP dan +1 Skor Mabar diberikan seluruh personel."
            )
            if callback.message.chat.type != "private":
                asyncio.create_task(set_auto_delete(conf_msg, None, 60))
                
    elif action == "leave":
        session, msg = await lfg_service.leave_session(session_id, callback.from_user.id)
        if not session:
            await callback.answer(f"⚠️ {msg}", show_alert=True)
            return
            
        if session.status == "closed" and callback.from_user.id == session.host_id:
            await callback.message.edit_text(f"<b>LFG DIBATALKAN</b>\nHost telah membatalkan sesi ini.")
        else:
            text, markup = await build_lfg_interface(session, user_service, callback.bot)
            await callback.message.edit_text(text, reply_markup=markup)
            
        await callback.answer(msg)

    elif action == "ping":
        session = await lfg_service.get_session(session_id)
        if not session or callback.from_user.id not in session.players:
            await callback.answer("Hanya personel skuad yang bisa melakukan PING.", show_alert=True)
            return
            
        ping_text = (
            f"<b>PEMBERITAHUAN SKUAD:</b>\n"
            f"Skuad <b>{session.host_name}</b> membutuhkan tambahan personel.\n"
            f"<b>Mode:</b> {session.lfg_type.upper()}\n"
            f"<b>Kekurangan:</b> {session.max_players - len(session.players)} Operator."
        )
        await callback.message.reply(ping_text)
        await callback.answer("Notifikasi dikirim.")
