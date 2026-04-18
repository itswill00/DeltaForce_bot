from aiogram import Router, types, F, Bot
from aiogram.filters import CommandStart, Command, ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import ChatMemberUpdated
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.user_db import user_db
from utils.style_utils import get_header, get_footer
from utils.auto_delete import set_auto_delete
import asyncio
import random
from datetime import datetime

router = Router()

def get_dashboard_kb(is_registered: bool = False, page: int = 1):
    builder = InlineKeyboardBuilder()
    if not is_registered:
        builder.button(text="🚀 DAFTAR SEKARANG", callback_data="start_register")
        builder.button(text="ℹ️ Panduan Bantuan", callback_data="main_help")
        builder.adjust(1)
    else:
        if page == 1:
            builder.button(text="👤 Profil Saya", callback_data="main_profile")
            builder.button(text="🕹️ Cari Teman Main", callback_data="main_mabar")
            builder.button(text="🔍 Lokasi & Barang", callback_data="main_intel")
            builder.button(text="🔫 Panduan Senjata", callback_data="main_meta")
            builder.button(text="➡️ Fitur Komunitas", callback_data="main_page_2")
            builder.adjust(2, 2, 1)
        else:
            builder.button(text="🏆 Papan Peringkat", callback_data="main_leaderboard")
            builder.button(text="🛒 Toko Item", callback_data="main_shop")
            builder.button(text="🧠 Kuis Taktis", callback_data="main_trivia")
            builder.button(text="🚑 Data Operator", callback_data="main_operator")
            builder.button(text="⬅️ Kembali ke Utama", callback_data="main_page_1")
            builder.adjust(2, 2, 1)
            
    return builder.as_markup()

def get_group_command_kb(bot_username: str = "DeltaForceHubBot"):
    builder = InlineKeyboardBuilder()
    builder.button(text="🕹️ Mulai Mabar", callback_data="main_mabar")
    builder.button(text="🧠 Kuis Trivia", callback_data="main_trivia")
    builder.button(text="🏆 Leaderboard", callback_data="main_leaderboard")
    builder.button(text="👤 Profil (DM)", url=f"https://t.me/{bot_username}?start=profile")
    builder.adjust(2)
    return builder.as_markup()

def get_tactical_briefing():
    tips = [
        "Selalu periksa titik ekstraksi cadangan sebelum memulai operasi.",
        "Item merah (Red Items) paling sering ditemukan di area dengan tingkat bahaya 'High'.",
        "Gunakan role Medic jika Anda bermain dalam tim besar untuk meningkatkan peluang bertahan hidup.",
        "Granat asap sangat efektif untuk menutupi gerakan saat melakukan looting di area terbuka.",
        "Pelajari rute 'Zero Dam' untuk ekstraksi paling aman bagi pemula.",
        "Mabar dalam skuad penuh memberikan bonus XP koordinasi lebih besar."
    ]
    return f"<b>📬 BRIEFING TAKTIS HARI INI:</b>\n<i>\"{random.choice(tips)}\"</i>"

@router.message(CommandStart())
@router.message(Command("menu", "dashboard"))
async def cmd_start(message: types.Message, command: CommandStart = None):
    if message.chat.type in ["group", "supergroup"]:
        bot_user = await message.bot.get_me()
        text = get_header("TACTICAL HUB ACTIVE", "📡")
        text += (
            f"Halo Personel <b>{message.chat.title}</b>!\n\n"
            "Gunakan <code>/cmd</code> untuk membuka menu taktis grup atau <code>/mabar</code> untuk mencari tim."
        )
        await message.answer(text, reply_markup=get_group_command_kb(bot_user.username))
        return
        
    user_id = message.from_user.id
    user_data = await user_db.get_user(user_id)
    is_reg = user_data and "ign" in user_data
    
    # 1. Handle Deep Linking
    if command and command.args:
        arg = command.args.strip().lower()
        if arg == "reg":
            from handlers.profile import cmd_register
            await cmd_register(message, None)
            return
        elif arg == "map":
            from handlers.intel import cmd_map
            await cmd_map(message)
            return
        elif arg == "shop":
            from handlers.shop import cmd_shop
            await cmd_shop(message)
            return
        elif arg == "profile":
            from handlers.profile import cmd_profile
            await cmd_profile(message)
            return

    # 2. Daily Briefing Logic
    briefing_text = ""
    if is_reg:
        today = datetime.now().date().isoformat()
        last_login = user_data.get("last_login", "")
        if today != last_login:
            briefing_text = get_tactical_briefing() + "\n\n"
            await user_db.update_last_login(user_id, today)

    # 3. Main Dashboard View
    text = get_header("DASHBOARD TAKTIS", "📱")
    if not is_reg:
        text += (
            f"Halo <b>{message.from_user.first_name}</b>!\n\n"
            "Selamat datang di Hub Komunitas Delta Force Indonesia.\n\n"
            "<b>🚀 3 LANGKAH CEPAT MEMULAI:</b>\n"
            "1️⃣ Klik tombol <b>Daftar Sekarang</b> di bawah.\n"
            "2️⃣ Masukkan nama in-game (IGN) Anda.\n"
            "3️⃣ Pilih role spesialisasi Anda.\n\n"
            "<i>Setelah terdaftar, semua fitur mabar dan intelijen akan terbuka otomatis!</i>"
        )
    else:
        level = user_data.get("level", 1)
        xp = user_data.get("xp", 0)
        text += briefing_text
        text += (
            f"Selamat datang kembali, <b>{user_data.get('ign')}</b>!\n"
            f"🏅 Level Ops: {level} | ✨ XP: {xp}\n\n"
            "Pilih menu di bawah ini:"
        )
    
    text += get_footer("Versi 3.0 Tactical Simplification")
    await message.answer(text, reply_markup=get_dashboard_kb(is_reg))

@router.callback_query(F.data == "main_menu")
@router.callback_query(F.data == "main_page_1")
async def process_main_menu(callback: types.CallbackQuery):
    user_data = await user_db.get_user(callback.from_user.id)
    is_reg = user_data and "ign" in user_data
    
    text = get_header("DASHBOARD TAKTIS", "📱")
    if not is_reg:
        text += (
            "<b>🚀 3 LANGKAH CEPAT MEMULAI:</b>\n"
            "1️⃣ Klik tombol <b>Daftar Sekarang</b> di bawah.\n"
            "2️⃣ Masukkan nama in-game (IGN) Anda.\n"
            "3️⃣ Pilih role spesialisasi Anda."
        )
    else:
        level = user_data.get("level", 1)
        xp = user_data.get("xp", 0)
        text += (
            f"Selamat datang kembali, <b>{user_data.get('ign')}</b>!\n"
            f"🏅 Level Ops: {level} | ✨ XP: {xp}\n\n"
            "Pilih menu di bawah (Halaman 1):"
        )
    
    text += get_footer("Versi 3.0 Dashboard Hub")
    await callback.message.edit_text(text, reply_markup=get_dashboard_kb(is_reg, page=1))
    await callback.answer()

@router.callback_query(F.data == "main_page_2")
async def process_main_page_2(callback: types.CallbackQuery):
    user_data = await user_db.get_user(callback.from_user.id)
    is_reg = user_data and "ign" in user_data
    
    if not is_reg:
        await callback.answer("Silakan daftar terlebih dahulu!", show_alert=True)
        return

    level = user_data.get("level", 1)
    xp = user_data.get("xp", 0)
    
    text = get_header("DASHBOARD TAKTIS", "📱")
    text += (
        f"Operator: <b>{user_data.get('ign')}</b>\n\n"
        "Menu Lainnya (Halaman 2):"
    )
    
    text += get_footer("Versi 3.0 Community Hub")
    await callback.message.edit_text(text, reply_markup=get_dashboard_kb(is_reg, page=2))
    await callback.answer()

@router.message(Command("cmd", "gmenu"))
async def cmd_group_menu(message: types.Message):
    if message.chat.type not in ["group", "supergroup"]:
        await cmd_start(message)
        return
        
    bot_user = await message.bot.get_me()
    text = get_header("COMMAND CENTER", "🕹️")
    text += (
        "<b>Status:</b> Operasional\n"
        "Pilih aksi taktis untuk grup ini:"
    )
    await message.answer(text, reply_markup=get_group_command_kb(bot_user.username))

@router.callback_query(F.data == "main_help")
async def process_main_help(callback: types.CallbackQuery):
    """Simplified Help Directory"""
    text = get_header("PANDUAN BANTUAN", "ℹ️")
    text += (
        "<b>Cari Teman Main:</b> Buat atau gabung tim untuk main bareng.\n"
        "<b>Lokasi & Barang:</b> Lihat peta dan lokasi item berharga.\n"
        "<b>Panduan Senjata:</b> Rekomendasi senjata dan modifikasi terbaik.\n"
        "<b>Toko Item:</b> Tukar koin Anda dengan pangkat atau item keren.\n"
        "<b>Kuis Taktis:</b> Jawab kuis untuk dapat XP dan Koin.\n\n"
        "<i>Klik tombol di bawah untuk kembali ke Dashboard Utama.</i>"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()
@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bot_added_to_chat(event: ChatMemberUpdated, bot: Bot):
    """Handler for when the bot is added to a group."""
    if event.chat.type not in ["group", "supergroup"]:
        return
        
    text = get_header("UNIT TAKTIS DEPLOYED", "🫡")
    text += (
        f"Halo Personel <b>{event.chat.title}</b>!\n\n"
        "Unit Hub Delta Force Indonesia telah aktif di grup ini untuk membantu koordinasi skuad dan kuis taktis.\n\n"
        "<b>Aksi Cepat:</b>\n"
        "• /mabar - Buka Lobi Skuad\n"
        "• /trivia - Simulasi Pengetahuan\n"
        "• /leaderboard - Papan Peringkat\n\n"
        "<i>Untuk pendaftaran dan profil pribadi, silakan hubungi saya melalui Private Chat.</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Hubungkan Profil (DM)", url=f"https://t.me/{(await bot.get_me()).username}?start=help")
    
    await bot.send_message(event.chat.id, text, reply_markup=builder.as_markup())
