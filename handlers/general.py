from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, Command, ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import ChatMemberUpdated, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import UserService
from services.system_service import SystemService
from config import settings
from utils.style_utils import get_header, get_footer, force_height
from views.dashboard_view import render_dashboard
import asyncio
import random
import logging
from datetime import datetime

router = Router()

def get_dashboard_kb(user_id: int, is_registered: bool = False, page: int = 1):
    builder = InlineKeyboardBuilder()
    is_owner = int(user_id) == int(settings.owner_id)
    
    if not is_registered:
        builder.button(text="◈ DAFTAR SEKARANG", callback_data="start_register")
        builder.button(text="◇ PANDUAN PENGGUNAAN", callback_data="main_help")
        if is_owner:
            builder.button(text="◈ COMMAND CENTER", callback_data="admin_dashboard")
        builder.adjust(1)
    else:
        if page == 1:
            builder.button(text="◇ PROFIL", callback_data="main_profile")
            builder.button(text="▣ CARI TIM", callback_data="main_mabar")
            builder.button(text="⬡ DATA INTEL", callback_data="main_intel")
            builder.button(text="⬢ LOADOUTS", callback_data="main_meta")
            builder.button(text="▹ MENU LAIN", callback_data="main_page_2")
            if is_owner:
                builder.button(text="◈ COMMAND CENTER", callback_data="admin_dashboard")
                builder.adjust(2, 2, 2)
            else:
                builder.adjust(2, 2, 1)
        else:
            builder.button(text="◈ PERINGKAT", callback_data="main_leaderboard")
            builder.button(text="⌬ BURSA ITEM", callback_data="main_shop")
            builder.button(text="⌬ SIMULASI", callback_data="main_trivia")
            builder.button(text="◇ OPERATOR", callback_data="main_operator")
            builder.button(text="◃ KEMBALI", callback_data="main_page_1")
            builder.adjust(2, 2, 1)
            
    return builder.as_markup()

def get_group_command_kb(bot_username: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="▣ CARI TIM MABAR", callback_data="main_mabar")
    builder.button(text="⌬ KUIS TRIVIA", callback_data="main_trivia")
    builder.button(text="◈ CEK PERINGKAT", callback_data="main_leaderboard")
    builder.button(text="◇ PROFIL (DM)", url=f"https://t.me/{bot_username}?start=profile")
    builder.adjust(2)
    return builder.as_markup()

async def safe_answer_photo(message: types.Message, photo: str, caption: str, reply_markup):
    """Answers with photo, falls back to text if photo fails."""
    try:
        await message.answer_photo(photo=photo, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        logging.warning(f"Photo delivery failed, falling back to text: {e}")
        await message.answer(text=caption, reply_markup=reply_markup)

@router.message(Command("help"))
async def cmd_help(message: types.Message, system_service: SystemService):
    if message.chat.type != "private": return
    banner = await system_service.get_banner("main")
    text = get_header("Pusat Bantuan", "◇")
    text += (
        "Selamat datang di panduan navigasi Delta Force Hub. Berikut perintah yang tersedia:\n\n"
        "<b>◇ Akun & Profil</b>\n"
        "• <code>/register</code> - Profil operator.\n"
        "• <code>/profile</code> - Level & statistik.\n"
        "• <code>/vouch</code> - Reputasi rekan.\n\n"
        "<b>▣ Aktivitas Grup</b>\n"
        "• <code>/mabar</code> - Cari teman.\n"
        "• <code>/trivia</code> - Kuis koin.\n"
        "• <code>/leaderboard</code> - Papan peringkat.\n\n"
        "<b>⬡ Lainnya</b>\n"
        "• <code>/op</code> - Database kemampuan operator.\n"
        "• <code>/menu</code> - Kembali ke menu utama."
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ MENU UTAMA", callback_data="main_menu")
    await safe_answer_photo(message, banner, text, builder.as_markup())

@router.callback_query(F.data == "close_msg")
async def process_close_msg(callback: types.CallbackQuery):
    try: await callback.message.delete()
    except Exception: await callback.answer("Pesan terlalu lama.", show_alert=True)
    await callback.answer()

@router.message(CommandStart())
@router.message(Command("menu", "dashboard"))
async def cmd_start(message: types.Message, user_service: UserService, system_service: SystemService, command: CommandStart = None):
    bot_user = await message.bot.get_me()
    user_id = message.from_user.id
    banner = await system_service.get_banner("main")
    
    if message.chat.type in ["group", "supergroup"]:
        text = get_header("Hub Taktis Aktif", "◈")
        text += f"Selamat datang di Hub Komunitas <b>{message.chat.title}</b>.\n\nGunakan perintah di bawah untuk memulai koordinasi skuad:"
        await safe_answer_photo(message, banner, text, get_group_command_kb(bot_user.username))
        return
        
    user_data = await user_service.get_user(user_id)
    is_reg = user_data and user_data.ign
    
    if command and hasattr(command, 'args') and command.args:
        arg = command.args.strip().lower()
        if arg == "reg":
            from handlers.profile import cmd_register
            await cmd_register(message, None, user_service)
            return
        elif arg == "profile":
            from handlers.profile import cmd_profile
            from services.content_service import ContentService
            await cmd_profile(message, user_service, ContentService())
            return
        elif arg == "help":
            await cmd_help(message, system_service)
            return

    text = render_dashboard(user_data, is_reg, page=1)
    await safe_answer_photo(message, banner, text, get_dashboard_kb(user_id=user_id, is_registered=is_reg))

@router.callback_query(F.data == "main_menu")
@router.callback_query(F.data == "main_page_1")
async def process_main_menu(callback: types.CallbackQuery, user_service: UserService, system_service: SystemService):
    user_data = await user_service.get_user(callback.from_user.id)
    is_reg = user_data and user_data.ign
    text = render_dashboard(user_data, is_reg, page=1)
    
    if callback.message.photo:
        try:
            await callback.message.edit_caption(caption=text, reply_markup=get_dashboard_kb(user_id=callback.from_user.id, is_registered=is_reg, page=1))
        except Exception:
            await callback.message.answer(text, reply_markup=get_dashboard_kb(user_id=callback.from_user.id, is_registered=is_reg, page=1))
    else:
        await callback.message.edit_text(text, reply_markup=get_dashboard_kb(user_id=callback.from_user.id, is_registered=is_reg, page=1))
    await callback.answer()

@router.callback_query(F.data == "main_page_2")
async def process_main_page_2(callback: types.CallbackQuery, user_service: UserService):
    user_data = await user_service.get_user(callback.from_user.id)
    is_reg = user_data and user_data.ign
    if not is_reg:
        await callback.answer("Silakan mendaftar terlebih dahulu.", show_alert=True)
        return
    text = render_dashboard(user_data, is_reg, page=2)
    
    if callback.message.photo:
        await callback.message.edit_caption(caption=text, reply_markup=get_dashboard_kb(user_id=callback.from_user.id, is_registered=is_reg, page=2))
    else:
        await callback.message.edit_text(text, reply_markup=get_dashboard_kb(user_id=callback.from_user.id, is_registered=is_reg, page=2))
    await callback.answer()

@router.message(Command("cmd", "gmenu"))
async def cmd_group_menu(message: types.Message, system_service: SystemService):
    if message.chat.type not in ["group", "supergroup"]: return
    bot_user = await message.bot.get_me()
    banner = await system_service.get_banner("main")
    text = get_header("Menu Grup", "▣") + "Pilih aksi cepat untuk grup ini:"
    await safe_answer_photo(message, banner, text, get_group_command_kb(bot_user.username))

@router.callback_query(F.data == "main_help")
async def process_main_help(callback: types.CallbackQuery):
    if callback.message.chat.type != "private":
        await callback.answer("Panduan lengkap tersedia di chat pribadi.", show_alert=True)
        return
    text = get_header("Pusat Bantuan", "◇")
    text += (
        "Selamat datang di panduan navigasi Delta Force Hub. Berikut perintah yang tersedia:\n\n"
        "<b>◇ Akun & Profil</b>\n"
        "• <code>/register</code> - Profil operator.\n"
        "• <code>/profile</code> - Level & statistik.\n"
        "• <code>/vouch</code> - Reputasi rekan.\n\n"
        "<b>▣ Aktivitas Grup</b>\n"
        "• <code>/mabar</code> - Cari teman.\n"
        "• <code>/trivia</code> - Kuis koin.\n"
        "• <code>/leaderboard</code> - Papan peringkat.\n\n"
        "<i>Gunakan tombol di bawah untuk kembali.</i>"
    )
    builder = InlineKeyboardBuilder().button(text="◃ KEMBALI", callback_data="main_menu")
    
    if callback.message.photo:
        await callback.message.edit_caption(caption=force_height(text, 10), reply_markup=builder.as_markup())
    else:
        await callback.message.edit_text(text=force_height(text, 10), reply_markup=builder.as_markup())
    await callback.answer()
