import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.user_db import user_db
from database.group_db import group_db
from utils.style_utils import get_header, get_footer
from utils.auto_delete import set_auto_delete

router = Router()

@router.message(Command("leaderboard"))
@router.callback_query(F.data == "main_leaderboard")
@router.callback_query(F.data.startswith("lb_"))
async def cmd_leaderboard(event: types.Message | types.CallbackQuery):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    
    # Check scope from callback or default
    scope = "global"
    if message.chat.type != "private":
        scope = "group" # Default to group in groups
        
    if is_callback and event.data.startswith("lb_"):
        scope = event.data.split("_")[1]
    
    # Local tracking if in group
    chat_id = message.chat.id
    if message.chat.type != "private":
        await group_db.register_group(chat_id, message.chat.title)
        await group_db.track_member(chat_id, event.from_user.id)

    # Fetch data based on scope
    if scope == "group" and message.chat.type != "private":
        group_info = await group_db.get_group(chat_id)
        member_ids = group_info.get("members", []) if group_info else []
        
        # Filter global players by those in this group (None-safe)
        all_users = await user_db.get_all_users() or {}
        group_players = [u for uid, u in all_users.items() if u and int(uid) in member_ids]
        
        top_mabar = sorted([u for u in group_players if u and "mabar_score" in u], key=lambda x: x["mabar_score"], reverse=True)[:5]
        top_trivia = sorted([u for u in group_players if u and "trivia_score" in u], key=lambda x: x["trivia_score"], reverse=True)[:5]
        title_suffix = f" (GRUP: {message.chat.title})"
    else:
        top_mabar = await user_db.get_top_players(5, "mabar_score")
        top_trivia = await user_db.get_top_players(5, "trivia_score")
        title_suffix = " (GLOBAL)"

    text = get_header(f"PAPAN PERINGKAT{title_suffix}", "🏆")
    
    # MABAR LEADERBOARD
    text += "⚔️ <b>TOP MABAR (OPERASI)</b>\n"
    if not top_mabar:
        text += "<i>Belum ada data di lingkup ini.</i>\n"
    else:
        for i, p in enumerate(top_mabar):
            ign = p.get("ign", "Unknown")
            score = p.get("mabar_score", 0)
            text += f"{i+1}. <b>{ign}</b>: {score} Mabar\n"
            
    # TRIVIA LEADERBOARD
    text += "\n🧠 <b>TOP TRIVIA (SKOR)</b>\n"
    if not top_trivia:
        text += "<i>Belum ada data di lingkup ini.</i>\n"
    else:
        for i, p in enumerate(top_trivia):
            ign = p.get("ign", "Unknown")
            score = p.get("trivia_score", 0)
            text += f"{i+1}. <b>{ign}</b>: {score} Poin\n"
            
    builder = InlineKeyboardBuilder()
    if scope == "global" and message.chat.type != "private":
        builder.button(text="📍 Lihat Peringkat Grup Ini", callback_data="lb_group")
    elif scope == "group":
        builder.button(text="🌍 Lihat Peringkat Global", callback_data="lb_global")
        
    if message.chat.type == "private":
        builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    builder.adjust(1)
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=builder.as_markup())
        await event.answer()
    else:
        resp = await event.answer(text, reply_markup=builder.as_markup())
        if message.chat.type != "private":
            asyncio.create_task(set_auto_delete(resp, message, 120))

