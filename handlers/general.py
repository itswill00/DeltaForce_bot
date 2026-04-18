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
        builder.button(text="◈ DAFTAR SEKARANG", callback_data="start_register")
        builder.button(text="◇ PANDUAN PENGGUNAAN", callback_data="main_help")
        builder.adjust(1)
    else:
        if page == 1:
            builder.button(text="◇ PROFIL", callback_data="main_profile")
            builder.button(text="▣ CARI TIM", callback_data="main_mabar")
            builder.button(text="⬡ DATA INTEL", callback_data="main_intel")
            builder.button(text="⬢ LOADOUTS", callback_data="main_meta")
            builder.button(text="▹ MENU LAIN", callback_data="main_page_2")
            builder.adjust(2, 2, 1)
        else:
            builder.button(text="◈ PERINGKAT", callback_data="main_leaderboard")
            builder.button(text="⌬ BURSA ITEM", callback_data="main_shop")
            builder.button(text="🧠 TRIVIA", callback_data="main_trivia")
            builder.button(text="🚑 OPERATOR", callback_data="main_operator")
            builder.button(text="◃ KEMBALI", callback_data="main_page_1")
            builder.adjust(2, 2, 1)
            
    return builder.as_markup()

def get_group_command_kb(bot_username: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="▣ CARI TIM MABAR", callback_data="main_mabar")
    builder.button(text="🧠 KUIS TRIVIA", callback_data="main_trivia")
    builder.button(text="◈ CEK PERINGKAT", callback_data="main_leaderboard")
    builder.button(text="◇ PROFIL (DM)", url=f"https://t.me/{bot_username}?start=profile")
    builder.adjust(2)
    return builder.as_markup()

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    if message.chat.type != "private": return

    text = get_header("Pusat Bantuan", "◇")
    text += (
        "Selamat datang di panduan navigasi Delta Force Hub. Berikut perintah yang tersedia:\n\n"
        "<b>◇ Akun & Profil</b>\n"
        "• <code>/register</code> - Pendaftaran profil operator.\n"
        "• <code>/profile</code> - Informasi level dan statistik.\n"
        "• <code>/vouch</code> - Memberikan reputasi ke rekan tim.\n\n"
        "<b>▣ Aktivitas Grup</b>\n"
        "• <code>/mabar</code> - Mencari teman untuk bermain bareng.\n"
        "• <code>/trivia</code> - Simulasi pengetahuan berhadiah koin.\n"
        "• <code>/leaderboard</code> - Papan peringkat operator.\n\n"
        "<b>⬡ Lainnya</b>\n"
        "• <code>/op</code> - Database kemampuan operator.\n"
        "• <code>/menu</code> - Kembali ke menu utama."
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ MENU UTAMA", callback_data="main_menu")

    await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data == "close_msg")
async def process_close_msg(callback: types.CallbackQuery):
    """Global handler to delete a message (Close button)."""
    try:
        await callback.message.delete()
    except Exception:
        # Fallback if message cannot be deleted (e.g. older than 48h)
        await callback.answer("Pesan terlalu lama untuk dihapus.", show_alert=True)
    await callback.answer()

@router.message(CommandStart())
async def cmd_start(message: types.Message, user_service: UserService, command: CommandStart):
    bot_user = await message.bot.get_me()
    
    if message.chat.type in ["group", "supergroup"]:
        text = get_header("Hub Taktis Aktif", "◈")
        text += (
            f"Selamat datang di Hub Komunitas <b>{message.chat.title}</b>.\n\n"
            "Gunakan perintah di bawah untuk memulai koordinasi skuad:"
        )
        await message.answer(text, reply_markup=get_group_command_kb(bot_user.username))
        return
        
    user_id = message.from_user.id
    user_data = await user_service.get_user(user_id)
    is_reg = user_data and user_data.ign
    
    if command and command.args:
        arg = command.args.strip().lower()
        if arg == "reg":
            from handlers.profile import cmd_register
            await cmd_register(message, None, user_service)
            return
        elif arg == "profile":
            from handlers.profile import cmd_profile
            await cmd_profile(message, user_service)
            return
        elif arg == "help":
            await cmd_help(message)
            return

    text = get_header("Delta Force Hub", "◈")
    
    if not is_reg:
        text += (
            f"Halo <b>{message.from_user.first_name}</b>! Selamat bergabung.\n\n"
            "Gunakan bot ini untuk mengelola profil, mencari teman mabar, "
            "dan bersaing di papan peringkat komunitas.\n\n"
            "Silakan daftarkan diri Anda untuk mulai mencatat statistik."
        )
    else:
        text += (
            f"Halo kembali, <b>{user_data.ign}</b>. Selamat datang di menu utama.\n\n"
            "Pilih layanan yang Anda butuhkan di bawah ini:"
        )
        
    text += "\n" + get_footer()
    await message.answer(text, reply_markup=get_dashboard_kb(is_reg))

@router.message(Command("menu", "dashboard"))
async def cmd_dashboard_manual(message: types.Message, user_service: UserService):
    if message.chat.type != "private": return
    await cmd_start(message, user_service, CommandStart())

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
        await callback.answer("Silakan mendaftar terlebih dahulu.", show_alert=True)
        return
    text = render_dashboard(user_data, is_reg, page=2)
    await callback.message.edit_text(text, reply_markup=get_dashboard_kb(is_reg, page=2))
    await callback.answer()

@router.message(Command("cmd", "gmenu"))
async def cmd_group_menu(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]: return
    bot_user = await message.bot.get_me()
    text = get_header("Menu Grup", "▣")
    text += "Pilih aksi cepat untuk grup ini:"
    await message.answer(text, reply_markup=get_group_command_kb(bot_user.username))

@router.callback_query(F.data == "main_help")
async def process_main_help(callback: types.CallbackQuery):
    if callback.message.chat.type != "private":
        await callback.answer("Panduan lengkap hanya tersedia di chat pribadi.", show_alert=True)
        return
    await cmd_help(callback.message)
    await callback.answer()
