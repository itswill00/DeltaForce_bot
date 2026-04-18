from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.user_service import UserService
from utils.group_logger import send_log
from utils.style_utils import get_header, get_footer
from handlers.shop import CATALOG
from views.profile_view import render_profile

router = Router()

ROLES = ["Assault", "Medic", "Engineer", "Recon"]

class RegisterState(StatesGroup):
    waiting_for_ign = State()
    waiting_for_role = State()

def get_role_keyboard():
    builder = InlineKeyboardBuilder()
    for role in ROLES:
        builder.button(text=f"🎯 {role}", callback_data=f"role_{role}")
    builder.button(text="❌ Batalkan", callback_data="main_menu")
    builder.adjust(2) 
    return builder.as_markup()

@router.message(Command("register"))
@router.callback_query(F.data == "start_register")
async def cmd_register(event: types.Message | types.CallbackQuery, state: FSMContext, user_service: UserService):
    user_id = event.from_user.id
    
    # Redirect if in Group
    message = event if isinstance(event, types.Message) else event.message
    if message.chat.type != "private":
        bot_user = await event.bot.get_me()
        text = "❌ <b>AKSES PRIBADI:</b> Registrasi hanya dapat dilakukan melalui chat pribadi untuk keamanan data."
        builder = InlineKeyboardBuilder()
        builder.button(text="🚀 Daftar di DM", url=f"https://t.me/{bot_user.username}?start=reg")
        await message.answer(text, reply_markup=builder.as_markup())
        return

    user_data = await user_service.get_user(user_id)
    if user_data and user_data.ign:
        text = f"✅ <b>KONFIRMASI:</b> Anda sudah terdaftar sebagai <b>{user_data.ign}</b>."
        builder = InlineKeyboardBuilder()
        builder.button(text="🏠 Menu Utama", callback_data="main_menu")
        if isinstance(event, types.CallbackQuery):
            await event.message.edit_text(text, reply_markup=builder.as_markup())
        else:
            await event.answer(text, reply_markup=builder.as_markup())
        return

    text = get_header("REGISTRASI OPERATOR", "📝")
    text += "Tentukan <b>In-Game Name (IGN)</b> Delta Force Anda sekarang (Maks 15 Karakter):"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Batalkan", callback_data="main_menu")
    
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=builder.as_markup())
        await event.answer()
    else:
        await event.answer(text, reply_markup=builder.as_markup())
        
    await state.set_state(RegisterState.waiting_for_ign)

@router.message(RegisterState.waiting_for_ign)
async def process_ign(message: types.Message, state: FSMContext):
    ign = message.text.strip()
    if len(ign) < 3 or len(ign) > 15:
        await message.answer("❌ Format IGN tidak valid. Minimal 3 hingga 15 karakter.")
        return
        
    await state.update_data(ign=ign)
    
    text = (
        f"✅ IGN dikonfirmasi: <b>{ign}</b>.\n"
        f"Langkah terakhir: Pilih <b>Role Utama</b> Anda:"
    )
    
    await message.answer(text, reply_markup=get_role_keyboard())
    await state.set_state(RegisterState.waiting_for_role)
    
    try:
        await message.delete()
    except Exception:
        pass

@router.callback_query(RegisterState.waiting_for_role, F.data.startswith("role_"))
async def process_role_selection(callback: types.CallbackQuery, state: FSMContext, user_service: UserService):
    role = callback.data.split("_")[1]
    
    state_data = await state.get_data()
    ign = state_data.get("ign", "Unknown")
    
    await user_service.register_user(
        user_id=callback.from_user.id,
        ign=ign,
        role=role,
        first_name=callback.from_user.first_name,
        username=callback.from_user.username
    )
    
    await send_log(
        callback.bot, 
        "NEW_USER", 
        f"Pengguna <b>{ign}</b> [{role}] terdaftar.\nID: {callback.from_user.id}"
    )
    
    await state.clear()
    
    text = get_header("PENDAFTARAN BERHASIL", "🚀")
    text += (
        f"Selamat bergabung, <b>{ign}</b>!\n\n"
        f"<b>Role:</b> {role}\n"
        f"<b>Status:</b> AKTIF (Terverifikasi)\n\n"
        "Anda sekarang dapat menggunakan fitur Mabar, Intel, dan Bursa Pangkat."
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📱 Buka Dashboard Utama", callback_data="main_menu")
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer("Registrasi Selesai!")

@router.message(Command("profile"))
@router.callback_query(F.data == "main_profile")
async def cmd_profile(event: types.Message | types.CallbackQuery, user_service: UserService):
    user_id = event.from_user.id
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event

    # Redirect if in Group
    if message.chat.type != "private":
        bot_user = await event.bot.get_me()
        text = "❌ <b>DATA PRIBADI:</b> Silakan cek profil Anda di chat pribadi agar tidak mengganggu grup."
        builder = InlineKeyboardBuilder()
        builder.button(text="👤 Buka Profil (DM)", url=f"https://t.me/{bot_user.username}?start=profile")
        await message.answer(text, reply_markup=builder.as_markup())
        return

    user_data = await user_service.get_user(user_id)
    if not user_data or not user_data.ign:
        text = "❌ Profil tidak ditemukan. Silakan daftar terlebih dahulu menggunakan tombol di bawah."
        builder = InlineKeyboardBuilder()
        builder.button(text="🚀 Daftar Sekarang", callback_data="start_register")
        builder.button(text="🏠 Menu Utama", callback_data="main_menu")
        
        if is_callback:
            await event.message.edit_text(text, reply_markup=builder.as_markup())
        else:
            await event.answer(text, reply_markup=builder.as_markup())
        return
        
    owned_ids = user_data.owned_items or []
    badges = []
    for oid in owned_ids:
        if oid in CATALOG:
            badges.append(CATALOG[oid]["name"])
    
    # Use the new View Layer
    profile_text = render_profile(user_data, badges)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    
    if is_callback:
        await event.message.edit_text(profile_text, reply_markup=builder.as_markup())
        await event.answer()
    else:
        await event.answer(profile_text, reply_markup=builder.as_markup())

@router.message(Command("vouch"))
async def cmd_vouch(message: types.Message, user_service: UserService):
    if not message.reply_to_message:
        await message.answer("❌ Balas pesan user yang ingin Anda beri reputasi (Vouch).")
        return
        
    target_user = message.reply_to_message.from_user
    if target_user.id == message.from_user.id:
        await message.answer("❌ Anda tidak bisa memberikan reputasi kepada diri sendiri.")
        return
        
    if target_user.is_bot:
        await message.answer("❌ Bot tidak membutuhkan reputasi.")
        return

    target_data = await user_service.get_user(target_user.id)
    if not target_data:
        await message.answer("❌ User tersebut belum terdaftar di sistem Tactical Hub.")
        return

    await user_service.add_rep(target_user.id, 1)
    await user_service.add_xp(message.from_user.id, 5)
    
    await message.answer(
        f"✅ <b>VOUCH BERHASIL</b>\n"
        f"Reputasi berhasil diberikan kepada <b>{target_data.ign}</b>.\n"
        f"Terima kasih telah membangun komunitas yang sehat!"
    )
    
    await send_log(
        message.bot, 
        "ADMIN_ACTION", 
        f"User <code>{message.from_user.id}</code> memberikan Vouch kepada <code>{target_user.id}</code>."
    )
