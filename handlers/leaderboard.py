import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import UserService
from services.group_service import GroupService
from services.system_service import SystemService
from utils.style_utils import get_header, get_footer, safe_edit_message
from utils.auto_delete import set_auto_delete

router = Router()

@router.message(Command("leaderboard"))
@router.callback_query(F.data == "main_leaderboard")
@router.callback_query(F.data.startswith("lb_"))
async def cmd_leaderboard(event: types.Message | types.CallbackQuery, user_service: UserService, group_service: GroupService, system_service: SystemService):
    is_cb = isinstance(event, types.CallbackQuery)
    message = event.message if is_cb else event
    
    scope = "global"
    if message.chat.type != "private":
        scope = "group"
    if is_cb and event.data.startswith("lb_"):
        scope = event.data.split("_")[1]
    
    if message.chat.type != "private":
        await group_service.register_group(message.chat.id, message.chat.title)
        await group_service.track_member(message.chat.id, event.from_user.id)

    if scope == "group" and message.chat.type != "private":
        group_info = await group_service.get_group(message.chat.id)
        member_ids = group_info.members if group_info else []
        resolved_players = []
        for uid in member_ids:
            u = await user_service.get_user(uid)
            if u: resolved_players.append(u)
        top_mabar = sorted(resolved_players, key=lambda x: x.mabar_score, reverse=True)[:5]
        top_trivia = sorted(resolved_players, key=lambda x: x.trivia_score, reverse=True)[:5]
        title_s = f"Grup: {message.chat.title}"
    else:
        top_mabar = await user_service.get_top_players(5, "mabar_score")
        top_trivia = await user_service.get_top_players(5, "trivia_score")
        title_s = "Global Command"

    text = get_header(f"Peringkat - {title_s}", "🏆")
    text += "⚔️ <b>Top Mabar (Operasi)</b>\n"
    if not top_mabar: text += "<i>Belum ada data.</i>\n"
    else:
        for i, p in enumerate(top_mabar):
            text += f"<code>{i+1}</code>. <b>{p.ign:10}</b> : <code>{p.mabar_score}</code>\n"
    text += "\n🧠 <b>Top Trivia (Skor)</b>\n"
    if not top_trivia: text += "<i>Belum ada data.</i>\n"
    else:
        for i, p in enumerate(top_trivia):
            text += f"<code>{i+1}</code>. <b>{p.ign:10}</b> : <code>{p.trivia_score}</code>\n"
            
    builder = InlineKeyboardBuilder()
    if scope == "global" and message.chat.type != "private":
        builder.button(text="📍 LIHAT PERINGKAT GRUP", callback_data="lb_group")
    elif scope == "group":
        builder.button(text="🌍 LIHAT PERINGKAT GLOBAL", callback_data="lb_global")
    if message.chat.type == "private":
        builder.button(text="🏠 KEMBALI KE MENU", callback_data="main_menu")
    builder.adjust(1)
    
    if is_cb:
        await safe_edit_message(event, text, builder.as_markup())
    else:
        banner = await system_service.get_banner("main")
        from handlers.general import safe_answer_photo
        await safe_answer_photo(event, banner, text, builder.as_markup())
        if message.chat.type != "private":
            asyncio.create_task(set_auto_delete(None, message, 120)) # Fixed auto_delete call
