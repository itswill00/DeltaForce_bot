from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import UserService
from services.lfg_service import LfgService
from config import settings
from utils.style_utils import get_header, get_footer
from utils.auto_delete import set_auto_delete
from views.lfg_view import render_lfg
import asyncio

router = Router()

@router.message(Command("mabar"))
@router.callback_query(F.data == "main_mabar")
async def cmd_mabar(event: types.Message | types.CallbackQuery, user_service: UserService):
    is_cb = isinstance(event, types.CallbackQuery)
    message = event.message if is_cb else event
    
    user_info = await user_service.get_user(event.from_user.id)
    if not user_info or not user_info.ign:
        text = "❌ <b>AKSES DITOLAK:</b> Kamu harus <code>/register</code> profil sebelum mabar."
        builder = InlineKeyboardBuilder().button(text="◈ DAFTAR SEKARANG", callback_data="start_register")
        if is_cb: await event.message.edit_caption(caption=text, reply_markup=builder.as_markup())
        else: await event.answer_photo(photo=settings.banner_lfg, caption=text, reply_markup=builder.as_markup())
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="🎮 Hazard Ops (3-P)", callback_data="lfghost_hazard")
    builder.button(text="⚔️ Havoc Warfare (4-P)", callback_data="lfghost_havoc")
    builder.button(text="◃ KEMBALI", callback_data="main_menu")
    builder.adjust(1)
    
    text = get_header("PENGATURAN MABAR", "🕹️") + "Pilih mode operasi skuad Anda:"
    if is_cb: await event.message.edit_caption(caption=text, reply_markup=builder.as_markup())
    else: await event.answer_photo(photo=settings.banner_lfg, caption=text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("lfghost_"))
async def process_lfg_host(callback: types.CallbackQuery, user_service: UserService, lfg_service: LfgService):
    lfg_type = callback.data.split("_")[1]
    user_info = await user_service.get_user(callback.from_user.id)
    host_name = user_info.ign if user_info else callback.from_user.first_name
    
    max_p = 3 if lfg_type == "hazard" else 4
    session = await lfg_service.create_session(callback.from_user.id, host_name, lfg_type, max_p)
    
    from utils.group_logger import send_log
    await send_log(callback.bot, "LFG_CREATED", f"<b>{host_name}</b> membuka lobi {lfg_type}.")
    
    text, markup = await build_lfg_interface(session, user_service, callback.bot)
    try: await callback.message.delete()
    except: pass
    
    lfg_msg = await callback.message.answer_photo(photo=settings.banner_lfg, caption=text, reply_markup=markup)
    await callback.answer("Sektor dibuka.")
    if callback.message.chat.type != "private":
        asyncio.create_task(set_auto_delete(lfg_msg, None, 600))

async def build_lfg_interface(session, user_service: UserService, bot):
    player_data = []
    for pid in session.players:
        u = await user_service.get_user(pid)
        player_data.append(f"<b>{u.ign}</b> (<code>{u.role}</code>)" if u else f"ID:<code>{pid}</code>")
    text = render_lfg(session, player_data)
    builder = InlineKeyboardBuilder()
    if session.status == "open":
        builder.button(text="➕ GABUNG", callback_data=f"lfg_join_{session.id}")
        builder.button(text="➖ KELUAR", callback_data=f"lfg_leave_{session.id}")
        builder.button(text="🔊 PING", callback_data=f"lfg_ping_{session.id}")
    builder.button(text="◇ PROFIL (DM)", url=f"https://t.me/{(await bot.get_me()).username}?start=profile")
    builder.adjust(2)
    return text, builder.as_markup()

@router.callback_query(F.data.startswith("lfg_"))
async def process_lfg_action(callback: types.CallbackQuery, user_service: UserService, lfg_service: LfgService):
    parts = callback.data.split("_")
    action, session_id = parts[1], parts[2]
    
    if action == "join":
        session, msg = await lfg_service.join_session(session_id, callback.from_user.id)
        if not session:
            await callback.answer(f"⚠️ {msg}", show_alert=True)
            return
        text, markup = await build_lfg_interface(session, user_service, callback.bot)
        await callback.message.edit_caption(caption=text, reply_markup=markup)
        await callback.answer(msg)
        if session.status == "closed":
            conf = await callback.message.answer(f"✅ <b>SKUAD SIAP: {session.host_name}</b>\nBonus XP & Mabar diberikan.")
            if callback.message.chat.type != "private": asyncio.create_task(set_auto_delete(conf, None, 60))
                
    elif action == "leave":
        session, msg = await lfg_service.leave_session(session_id, callback.from_user.id)
        if not session:
            await callback.answer(f"⚠️ {msg}", show_alert=True)
            return
        if session.status == "closed" and callback.from_user.id == session.host_id:
            await callback.message.edit_caption(caption="<b>LOBAL DIBATALKAN</b>\nHost telah membatalkan sesi.")
        else:
            text, markup = await build_lfg_interface(session, user_service, callback.bot)
            await callback.message.edit_caption(caption=text, reply_markup=markup)
        await callback.answer(msg)

    elif action == "ping":
        session = await lfg_service.get_session(session_id)
        if not session or callback.from_user.id not in session.players:
            await callback.answer("Akses ditolak.", show_alert=True)
            return
        await callback.message.reply(f"<b>PEMBERITAHUAN SKUAD:</b>\nSkuad <b>{session.host_name}</b> butuh {session.max_players - len(session.players)} operator.")
        await callback.answer("Ping terkirim.")
