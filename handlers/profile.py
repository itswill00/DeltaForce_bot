from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.user_service import UserService
from services.content_service import ContentService
from config import settings
from utils.group_logger import send_log
from utils.style_utils import get_header, get_footer
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
    builder.button(text="◃ BATAL", callback_data="main_menu")
    builder.adjust(2) 
    return builder.as_markup()

@router.message(Command("register"))
@router.callback_query(F.data == "start_register")
async def cmd_register(event: types.Message | types.CallbackQuery, state: FSMContext, user_service: UserService):
    user_id = event.from_user.id
    message = event if isinstance(event, types.Message) else event.message
    
    if message.chat.type != "private":
        bot_user = await event.bot.get_me()
        text = "❌ <b>AKSES PRIBADI:</b> Registrasi hanya dapat dilakukan melalui chat pribadi."
        builder = InlineKeyboardBuilder().button(text="◈ DAFTAR DI DM", url=f"https://t.me/{bot_user.username}?start=reg")
        await message.answer(text, reply_markup=builder.as_markup())
        return

    user_data = await user_service.get_user(user_id)
    if user_data and user_data.ign:
        text = f"✅ <b>KONFIRMASI:</b> Anda sudah terdaftar sebagai <b>{user_data.ign}</b>."
        builder = InlineKeyboardBuilder().button(text="◃ MENU UTAMA", callback_data="main_menu")
        if isinstance(event, types.CallbackQuery): await event.message.edit_caption(caption=text, reply_markup=builder.as_markup())
        else: await event.answer_photo(photo=settings.banner_profile, caption=text, reply_markup=builder.as_markup())
        return

    text = get_header("REGISTRASI OPERATOR", "📝") + "Tentukan <b>Call-sign (IGN)</b> kamu sekarang (Maks 15 Karakter):"
    builder = InlineKeyboardBuilder().button(text="◃ BATAL", callback_data="main_menu")
    
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_caption(caption=text, reply_markup=builder.as_markup())
    else:
        await event.answer_photo(photo=settings.banner_profile, caption=text, reply_markup=builder.as_markup())
    await state.set_state(RegisterState.waiting_for_ign)

@router.message(RegisterState.waiting_for_ign)
async def process_ign(message: types.Message, state: FSMContext):
    ign = message.text.strip()
    if len(ign) < 3 or len(ign) > 15:
        await message.answer("❌ Minimal 3 hingga 15 karakter.")
        return
    await state.update_data(ign=ign)
    await message.answer(f"✅ IGN dikonfirmasi: <b>{ign}</b>.\nPilih <b>Role Utama</b> Anda:", reply_markup=get_role_keyboard())
    await state.set_state(RegisterState.waiting_for_role)

@router.callback_query(RegisterState.waiting_for_role, F.data.startswith("role_"))
async def process_role_selection(callback: types.CallbackQuery, state: FSMContext, user_service: UserService):
    role = callback.data.split("_")[1]
    state_data = await state.get_data()
    ign = state_data.get("ign", "Unknown")
    await user_service.register_user(user_id=callback.from_user.id, ign=ign, role=role, first_name=callback.from_user.first_name, username=callback.from_user.username)
    await send_log(callback.bot, "NEW_USER", f"Pengguna <b>{ign}</b> [{role}] terdaftar.")
    await state.clear()
    
    text = get_header("PENDAFTARAN BERHASIL", "◈") + f"Selamat bergabung, <b>{ign}</b>!\n\nStatus kamu sekarang AKTIF."
    builder = InlineKeyboardBuilder().button(text="◃ MENU UTAMA", callback_data="main_menu")
    await callback.message.edit_caption(caption=text, reply_markup=builder.as_markup())
    await callback.answer("Registrasi Selesai!")

@router.message(Command("profile"))
@router.callback_query(F.data == "main_profile")
async def cmd_profile(event: types.Message | types.CallbackQuery, user_service: UserService, content_service: ContentService):
    user_id = event.from_user.id
    is_cb = isinstance(event, types.CallbackQuery)
    message = event.message if is_cb else event

    if message.chat.type != "private":
        bot_user = await event.bot.get_me()
        text = "❌ <b>DATA PRIBADI:</b> Silakan cek profil Anda di chat pribadi."
        builder = InlineKeyboardBuilder().button(text="◇ PROFIL (DM)", url=f"https://t.me/{bot_user.username}?start=profile")
        await message.answer(text, reply_markup=builder.as_markup())
        return

    user_data = await user_service.get_user(user_id)
    if not user_data or not user_data.ign:
        text = "❌ Profil tidak ditemukan. Silakan daftar terlebih dahulu."
        builder = InlineKeyboardBuilder().button(text="◈ DAFTAR SEKARANG", callback_data="start_register")
        if is_cb: await event.message.edit_caption(caption=text, reply_markup=builder.as_markup())
        else: await event.answer_photo(photo=settings.banner_profile, caption=text, reply_markup=builder.as_markup())
        return
        
    equipped_name = None
    if user_data.equipped_badge:
        shop_items = await content_service.get_shop_items()
        badge_info = shop_items.get(user_data.equipped_badge)
        if badge_info: equipped_name = badge_info.get("name")
    
    profile_text = render_profile(user_data, equipped_name)
    builder = InlineKeyboardBuilder()
    builder.button(text="🎒 INVENTORI", callback_data="shop_inventory")
    builder.button(text="◃ KEMBALI KE MENU", callback_data="main_menu")
    builder.adjust(1)
    
    if is_cb: await event.message.edit_caption(caption=profile_text, reply_markup=builder.as_markup())
    else: await event.answer_photo(photo=settings.banner_profile, caption=profile_text, reply_markup=builder.as_markup())
