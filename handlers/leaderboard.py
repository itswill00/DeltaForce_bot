import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import UserService
from services.group_service import GroupService
from utils.style_utils import get_header, get_footer, get_divider, format_field
from utils.auto_delete import set_auto_delete

router = Router()

@router.message(Command("leaderboard"))
@router.callback_query(F.data == "main_leaderboard")
@router.callback_query(F.data.startswith("lb_"))
async def cmd_leaderboard(event: types.Message | types.CallbackQuery, user_service: UserService, group_service: GroupService):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    
    scope = "global"
    if message.chat.type != "private":
        scope = "group"
        
    if is_callback and event.data.startswith("lb_"):
        scope = event.data.split("_")[1]
    
    chat_id = message.chat.id
    if message.chat.type != "private":
        await group_service.register_group(chat_id, message.chat.title)
        await group_service.track_member(chat_id, event.from_user.id)

    if scope == "group" and message.chat.type != "private":
        group_info = await group_service.get_group(chat_id)
        member_ids = group_info.members if group_info else []
        resolved_players = []
        for uid in member_ids:
            u = await user_service.get_user(uid)
            if u: resolved_players.append(u)
            
        top_mabar = sorted(resolved_players, key=lambda x: x.mabar_score, reverse=True)[:5]
        top_trivia = sorted(resolved_players, key=lambda x: x.trivia_score, reverse=True)[:5]
        title_suffix = f"LOCAL: {message.chat.title}"
    else:
        top_mabar = await user_service.get_top_players(5, "mabar_score")
        top_trivia = await user_service.get_top_players(5, "trivia_score")
        title_suffix = "GLOBAL COMMAND"

    text = get_header(f"RANKINGS: {title_suffix}", "🏆")
    
    text += "⚔️ <b>TOP OPERATORS (SQUAD)</b>\n"
    if not top_mabar:
        text += "<i>No data available.</i>\n"
    else:
        for i, p in enumerate(top_mabar):
            text += f"<code>{i+1:02}</code>. <b>{p.ign:12}</b> | <code>{p.mabar_score:3}</code> Ops\n"
            
    text += get_divider()
    text += "🧠 <b>TOP ANALYSTS (TRIVIA)</b>\n"
    if not top_trivia:
        text += "<i>No data available.</i>\n"
    else:
        for i, p in enumerate(top_trivia):
            text += f"<code>{i+1:02}</code>. <b>{p.ign:12}</b> | <code>{p.trivia_score:3}</code> Pts\n"
            
    text += get_divider()
    builder = InlineKeyboardBuilder()
    if scope == "global" and message.chat.type != "private":
        builder.button(text="📍 LOCAL RANKINGS", callback_data="lb_group")
    elif scope == "group":
        builder.button(text="🌍 GLOBAL RANKINGS", callback_data="lb_global")
        
    if message.chat.type == "private":
        builder.button(text="🏠 HUB MENU", callback_data="main_menu")
    builder.adjust(1)
    
    text += get_footer("Tactical Ranking System")
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=builder.as_markup())
        await event.answer()
    else:
        resp = await event.answer(text, reply_markup=builder.as_markup())
        if message.chat.type != "private":
            asyncio.create_task(set_auto_delete(resp, message, 120))
