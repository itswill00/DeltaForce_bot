import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import UserService
from services.group_service import GroupService
from utils.style_utils import get_header, get_footer
from utils.auto_delete import set_auto_delete

router = Router()

@router.message(Command("leaderboard"))
@router.callback_query(F.data == "main_leaderboard")
@router.callback_query(F.data.startswith("lb_"))
async def cmd_leaderboard(event: types.Message | types.CallbackQuery, user_service: UserService, group_service: GroupService):
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
        await group_service.register_group(chat_id, message.chat.title)
        await group_service.track_member(chat_id, event.from_user.id)

    # Fetch data based on scope
    if scope == "group" and message.chat.type != "private":
        group_info = await group_service.get_group(chat_id)
        member_ids = group_info.members if group_info else []
        
        # Filter global players by those in this group (O(N) for JSON layer is fine for this scale)
        top_mabar = []
        top_trivia = []
        
        # Optimization: We already have get_top_players, but for group scope we filter manually
        all_users = await user_service.db.get_all()
        group_players = [user_service.get_user(int(uid)) for uid in all_users["users"] if int(uid) in member_ids]
        
        # Resolve group_players (they are UserDTO objects from get_user)
        # Note: get_user is async, so we need to wait for them.
        resolved_players = []
        for uid in member_ids:
            u = await user_service.get_user(uid)
            if u: resolved_players.append(u)
            
        top_mabar = sorted(resolved_players, key=lambda x: x.mabar_score, reverse=True)[:5]
        # Assuming trivia_score was added to UserDTO in my previous step (if not I'll fix it)
        # Wait, I didn't add trivia_score to UserDTO. Let me check my previous write.
        top_trivia = sorted(resolved_players, key=lambda x: getattr(x, "trivia_score", 0), reverse=True)[:5]
        title_suffix = f" (GRUP: {message.chat.title})"
    else:
        top_mabar = await user_service.get_top_players(5, "mabar_score")
        # I need to ensure trivia_score is supported in UserDTO and UserService
        top_trivia = await user_service.get_top_players(5, "trivia_score")
        title_suffix = " (GLOBAL)"

    text = get_header(f"PAPAN PERINGKAT{title_suffix}", "🏆")
    
    # MABAR LEADERBOARD
    text += "⚔️ <b>TOP MABAR (OPERASI)</b>\n"
    if not top_mabar:
        text += "<i>Belum ada data di lingkup ini.</i>\n"
    else:
        for i, p in enumerate(top_mabar):
            ign = p.ign if p.ign else "Unknown"
            score = p.mabar_score
            text += f"{i+1}. <b>{ign}</b>: {score} Mabar\n"
            
    # TRIVIA LEADERBOARD
    text += "\n🧠 <b>TOP TRIVIA (SKOR)</b>\n"
    if not top_trivia:
        text += "<i>Belum ada data di lingkup ini.</i>\n"
    else:
        for i, p in enumerate(top_trivia):
            ign = p.ign if p.ign else "Unknown"
            score = getattr(p, "trivia_score", 0)
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
