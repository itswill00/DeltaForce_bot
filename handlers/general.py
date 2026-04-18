from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, Command, ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import ChatMemberUpdated
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import UserService
from utils.style_utils import get_header, get_footer
from utils.auto_delete import set_auto_delete
from views.dashboard_view import render_dashboard
import asyncio
import random
from datetime import datetime

router = Router()

def get_dashboard_kb(is_registered: bool = False, page: int = 1):
    builder = InlineKeyboardBuilder()
    if not is_registered:
        builder.button(text="🚀 INITIALIZE PROFILE", callback_data="start_register")
        builder.button(text="ℹ️ HELP CENTER", callback_data="main_help")
        builder.adjust(1)
    else:
        if page == 1:
            builder.button(text="👤 PROFILE", callback_data="main_profile")
            builder.button(text="🕹️ FIND SQUAD", callback_data="main_mabar")
            builder.button(text="🔍 INTEL DATA", callback_data="main_intel")
            builder.button(text="🔫 LOADOUTS", callback_data="main_meta")
            builder.button(text="➡️ NEXT PAGE", callback_data="main_page_2")
            builder.adjust(2, 2, 1)
        else:
            builder.button(text="🏆 RANKINGS", callback_data="main_leaderboard")
            builder.button(text="🛒 SUPPLY DROP", callback_data="main_shop")
            builder.button(text="🧠 SIMULATION", callback_data="main_trivia")
            builder.button(text="🚑 OPERATORS", callback_data="main_operator")
            builder.button(text="⬅️ BACK", callback_data="main_page_1")
            builder.adjust(2, 2, 1)
            
    return builder.as_markup()

def get_group_command_kb(bot_username: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="🕹️ FIND SQUAD", callback_data="main_mabar")
    builder.button(text="🧠 TRIVIA", callback_data="main_trivia")
    builder.button(text="🏆 RANKINGS", callback_data="main_leaderboard")
    builder.button(text="👤 PROFILE (DM)", url=f"https://t.me/{bot_username}?start=profile")
    builder.adjust(2)
    return builder.as_markup()

def get_tactical_briefing():
    tips = [
        "Always verify extraction points before engagement.",
        "Red Items are concentrated in high-threat sectors.",
        "Medic roles crucial for squad sustainability.",
        "Smoke grenades provide essential cover for loots.",
        "Zero Dam route prioritized for secure extraction.",
        "Full squad deployment yields coordination XP bonus."
    ]
    return random.choice(tips)

@router.message(CommandStart())
@router.message(Command("menu", "dashboard"))
async def cmd_start(message: types.Message, user_service: UserService, command: CommandStart = None):
    bot_user = await message.bot.get_me()
    if message.chat.type in ["group", "supergroup"]:
        text = get_header("TACTICAL HUB ACTIVE", "📡")
        text += (
            f"Authorized Hub for <b>{message.chat.title}</b>!\n\n"
            "Use <code>/cmd</code> for group menu or <code>/mabar</code> to initiate squad search."
        )
        await message.answer(text, reply_markup=get_group_command_kb(bot_user.username))
        return
        
    user_id = message.from_user.id
    user_data = await user_service.get_user(user_id)
    is_reg = user_data and user_data.ign
    
    # Handle Deep Linking
    if command and command.args:
        arg = command.args.strip().lower()
        if arg == "reg":
            from handlers.profile import cmd_register
            return
        elif arg == "profile":
            from handlers.profile import cmd_profile
            await cmd_profile(message, user_service)
            return

    # Daily Briefing
    briefing = None
    if is_reg:
        today = datetime.now().date().isoformat()
        if today != user_data.last_login:
            briefing = get_tactical_briefing()
            await user_service.update_last_login(user_id)

    # Use the new View
    text = render_dashboard(user_data, is_reg, briefing=briefing, page=1)
    await message.answer(text, reply_markup=get_dashboard_kb(is_reg))

@router.callback_query(F.data == "main_menu")
@router.callback_query(F.data == "main_page_1")
async def process_main_menu(callback: types.CallbackQuery, user_service: UserService):
    user_data = await user_service.get_user(callback.from_user.id)
    is_reg = user_data and user_data.ign
    
    text = render_dashboard(user_data, is_reg, page=1)
    await callback.message.edit_text(text, reply_markup=get_dashboard_kb(is_reg, page=1))
    await callback.answer()

@router.callback_query(F.data == "main_page_2")
async def process_main_page_2(callback: types.CallbackQuery, user_service: UserService):
    user_data = await user_service.get_user(callback.from_user.id)
    is_reg = user_data and user_data.ign
    
    if not is_reg:
        await callback.answer("Authorization failed: Register first.", show_alert=True)
        return

    text = render_dashboard(user_data, is_reg, page=2)
    await callback.message.edit_text(text, reply_markup=get_dashboard_kb(is_reg, page=2))
    await callback.answer()

@router.message(Command("cmd", "gmenu"))
async def cmd_group_menu(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
        
    bot_user = await message.bot.get_me()
    text = get_header("COMMAND CENTER", "🕹️")
    text += "Hub operational. Select deployment actions:"
    await message.answer(text, reply_markup=get_group_command_kb(bot_user.username))

@router.callback_query(F.data == "main_help")
async def process_main_help(callback: types.CallbackQuery):
    text = get_header("TACTICAL HANDBOOK", "ℹ️")
    text += (
        "<b>FIND SQUAD:</b> Coordinate with local operators.\n"
        "<b>INTEL DATA:</b> Map intel and loot locations.\n"
        "<b>LOADOUTS:</b> Recommended weapon configurations.\n"
        "<b>SUPPLY DROP:</b> Exchange coins for honorary badges.\n"
        "<b>SIMULATION:</b> Tactical knowledge assessment.\n\n"
        "<i>Contact Central Command for further assistance.</i>"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 HUB MENU", callback_data="main_menu")
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()
