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
        builder.button(text="🚀 BUAT ID OPERATOR SEKARANG", callback_data="start_register")
        builder.button(text="ℹ️ CARA PENGGUNAAN", callback_data="main_help")
        builder.adjust(1)
    else:
        if page == 1:
            builder.button(text="👤 PROFIL SAYA", callback_data="main_profile")
            builder.button(text="🕹️ CARI TEMAN MAIN", callback_data="main_mabar")
            builder.button(text="🔍 INFO INTEL", callback_data="main_intel")
            builder.button(text="🔫 REKOMENDASI SENJATA", callback_data="main_meta")
            builder.button(text="➡️ MENU LANJUTAN", callback_data="main_page_2")
            builder.adjust(2, 2, 1)
        else:
            builder.button(text="🏆 PAPAN PERINGKAT", callback_data="main_leaderboard")
            builder.button(text="🛒 BURSA ITEM", callback_data="main_shop")
            builder.button(text="🧠 KUIS TRIVIA", callback_data="main_trivia")
            builder.button(text="🚑 DATA OPERATOR", callback_data="main_operator")
            builder.button(text="⬅️ KEMBALI", callback_data="main_page_1")
            builder.adjust(2, 2, 1)
            
    return builder.as_markup()

def get_group_command_kb(bot_username: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="🕹️ CARI TEMAN MABAR", callback_data="main_mabar")
    builder.button(text="🧠 TRIVIA", callback_data="main_trivia")
    builder.button(text="🏆 LEADERBOARD", callback_data="main_leaderboard")
    builder.button(text="👤 PROFIL (DM)", url=f"https://t.me/{bot_username}?start=profile")
    builder.adjust(2)
    return builder.as_markup()

def get_tactical_briefing():
    tips = [
        "Jangan lupa cek rute ekstraksi sebelum mulai perang ya!",
        "Item Merah biasanya ngumpul di area yang tingkat bahayanya tinggi.",
        "Role Medic itu penting banget biar tim bisa bertahan lama.",
        "Granat asap bisa jadi penolong pas lagi mau looting di tempat terbuka.",
        "Coba deh lewat rute Zero Dam kalau mau ekstraksi yang lebih aman.",
        "Main bareng skuad penuh dapet bonus XP lebih gede lho!"
    ]
    return random.choice(tips)

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Panduan Bantuan - Hanya aktif di Private Chat."""
    if message.chat.type != "private":
        return

    text = get_header("Pusat Bantuan", "❓")
    text += (
        "Halo Rekan! Butuh bantuan navigasi? Berikut panduan penggunaan bot Delta Force Hub:\n\n"
        "<b>👤 Akun & Profil</b>\n"
        "• <code>/register</code> - Daftar profil komunitas kamu.\n"
        "• <code>/profile</code> - Cek level, XP, dan statistik kamu.\n"
        "• <code>/vouch</code> (Reply) - Berikan Reputasi ke rekan setim.\n\n"
        "<b>🕹️ Aktivitas Grup</b>\n"
        "• <code>/mabar</code> - Buka lobi cari teman main.\n"
        "• <code>/trivia</code> - Mulai kuis taktis berhadiah koin.\n"
        "• <code>/leaderboard</code> - Cek peringkat operator global/grup.\n\n"
        "<b>🛠️ Lainnya</b>\n"
        "• <code>/op</code> - Lihat database skill operator.\n"
        "• <code>/menu</code> - Buka Dashboard utama.\n\n"
        "<i>Tips: Gunakan tombol-tombol di Dashboard untuk navigasi yang lebih mudah!</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 KEMBALI KE MENU", callback_data="main_menu")
    
    await message.answer(text, reply_markup=builder.as_markup())

@router.message(CommandStart())
async def cmd_start(message: types.Message, user_service: UserService, command: CommandStart):
    bot_user = await message.bot.get_me()
    
    # 1. LOGIKA GRUP
    if message.chat.type in ["group", "supergroup"]:
        text = get_header("PUSAT KOMANDO AKTIF", "📡")
        text += (
            f"Halo Rekan-rekan di <b>{message.chat.title}</b>! 👋\n\n"
            "Saya adalah unit pendukung taktis yang akan bantu kalian koordinasi mabar, kuis, dan pantau peringkat operator.\n\n"
            "<b>Cepat Terjun:</b>\n"
            "• Ketik <code>/mabar</code> buat cari tim.\n"
            "• Ketik <code>/cmd</code> buat menu lainnya."
        )
        await message.answer(text, reply_markup=get_group_command_kb(bot_user.username))
        return
        
    # 2. LOGIKA PRIVATE MESSAGE (DM)
    user_id = message.from_user.id
    user_data = await user_service.get_user(user_id)
    is_reg = user_data and user_data.ign
    
    # Handle Deep Linking (Referral/Action specific)
    if command and command.args:
        arg = command.args.strip().lower()
        if arg == "reg":
            # Pass directly to register flow in handlers/profile.py
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

    # Onboarding Style for DM
    text = get_header("Pusat Komando Delta Force", "🏠")
    
    if not is_reg:
        text += (
            f"Halo, <b>{message.from_user.first_name}</b>! 👋\n\n"
            "Senang sekali kamu mampir ke Markas Besar komunitas kita. Di sini, kamu bisa:\n"
            "⚔️ <b>Cari Skuad Mabar</b> yang kompak dan rapi.\n"
            "🏅 <b>Kumpulkan XP & Badge</b> prestasi permanen.\n"
            "🧠 <b>Ikut Kuis Trivia</b> buat asah taktik.\n\n"
            "Tapi sebelum terjun ke lapangan, yuk buat <b>ID OPERATOR</b> komunitas kamu dulu. "
            "Cuma butuh 10 detik kok!"
        )
    else:
        # Briefing harian untuk user terdaftar
        today = datetime.now().date().isoformat()
        briefing = ""
        if today != user_data.last_login:
            tip = get_tactical_briefing()
            briefing = f"📬 <b>Briefing Hari Ini:</b>\n<i>\"{tip}\"</i>\n\n"
            await user_service.update_last_login(user_id)
            
        text += (
            f"Halo kembali, <b>{user_data.ign}</b>! 🫡\n"
            f"Status kamu saat ini: <b>Level {user_data.level}</b>\n\n"
            f"{briefing}"
            "Apa rencana misi kita hari ini? Pilih menu di bawah ya:"
        )
        
    text += "\n" + get_footer("Tactical Onboarding v4.0")
    await message.answer(text, reply_markup=get_dashboard_kb(is_reg))

@router.message(Command("menu", "dashboard"))
async def cmd_dashboard_manual(message: types.Message, user_service: UserService):
    """Fallback if user types /menu manually."""
    if message.chat.type != "private": return
    # Reuse start logic without deep-link handling
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
        await callback.answer("Daftar dulu yuk biar bisa akses menu ini!", show_alert=True)
        return

    text = render_dashboard(user_data, is_reg, page=2)
    await callback.message.edit_text(text, reply_markup=get_dashboard_kb(is_reg, page=2))
    await callback.answer()

@router.message(Command("cmd", "gmenu"))
async def cmd_group_menu(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        return
        
    bot_user = await message.bot.get_me()
    text = get_header("PUSAT KOMANDO", "🕹️")
    text += "Unit operasional siap mendukung misi. Mau ngapain kita di grup ini?"
    await message.answer(text, reply_markup=get_group_command_kb(bot_user.username))

@router.callback_query(F.data == "main_help")
async def process_main_help(callback: types.CallbackQuery):
    if callback.message.chat.type != "private":
        await callback.answer("Panduan detail hanya tersedia di Private Message (DM).", show_alert=True)
        return
        
    await cmd_help(callback.message)
    await callback.answer()
