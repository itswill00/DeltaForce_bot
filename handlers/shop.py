from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import UserService
from services.content_service import ContentService
from utils.style_utils import get_header, get_footer, format_field, get_divider

router = Router()

@router.message(Command("shop"))
@router.callback_query(F.data == "main_shop")
async def cmd_shop(event: types.Message | types.CallbackQuery, user_service: UserService, content_service: ContentService):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    user_id = event.from_user.id
    
    if message.chat.type != "private":
        bot_user = await event.bot.get_me()
        text = "⌬ <b>BURSA ITEM:</b> Akses ditolak. Transaksi hanya diizinkan melalui saluran privat."
        builder = InlineKeyboardBuilder()
        builder.button(text="⌬ BUKA BURSA (DM)", url=f"https://t.me/{bot_user.username}?start=shop")
        await message.answer(text, reply_markup=builder.as_markup())
        return

    user_data = await user_service.get_user(user_id)
    if not user_data or not user_data.ign:
        text = "❌ Silakan daftarkan Call-sign kamu terlebih dahulu sebelum mengakses bursa."
        builder = InlineKeyboardBuilder()
        builder.button(text="◈ DAFTAR SEKARANG", callback_data="start_register")
        builder.button(text="◃ KEMBALI KE MENU", callback_data="main_menu")
        if is_callback: await event.message.edit_text(text, reply_markup=builder.as_markup())
        else: await event.answer(text, reply_markup=builder.as_markup())
        return
        
    text = get_header("Bursa Item & Supply", "⌬")
    text += format_field("SALDO KREDIT", f"{user_data.balance} Koin")
    text += get_divider()
    text += "Silakan pilih item yang tersedia:"
    
    catalog = await content_service.get_shop_items()
    
    builder = InlineKeyboardBuilder()
    for item_id, item in catalog.items():
        builder.button(text=f"‣ {item['name']} ({item['price']})", callback_data=f"buy_{item_id}")
    
    builder.button(text="🎒 BUKA INVENTORI", callback_data="shop_inventory")
    builder.button(text="◃ MENU UTAMA", callback_data="main_menu")
    builder.adjust(1)
    
    from utils.style_utils import force_height
    text = force_height(text, 12)
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=builder.as_markup())
        await event.answer()
    else:
        await event.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery, user_service: UserService, content_service: ContentService):
    item_id = callback.data.replace("buy_", "")
    catalog = await content_service.get_shop_items()
    item = catalog.get(item_id)
    
    if not item: 
        await callback.answer("❌ Item tidak tersedia.", show_alert=True)
        return
        
    user_data = await user_service.get_user(callback.from_user.id)
    if not user_data: return
    
    if user_data.balance < item["price"]:
        await callback.answer(f"❌ Saldo tidak cukup! Butuh {item['price']} Koin.", show_alert=True)
        return
        
    owned_items = user_data.owned_items or []
    if item_id in owned_items:
        await callback.answer("⚠️ Kamu sudah punya item ini.", show_alert=True)
        return
        
    owned_items.append(item_id)
    await user_service.add_balance(callback.from_user.id, -item["price"])
    await user_service.update_user(callback.from_user.id, {"owned_items": owned_items})
    
    await callback.answer(f"✅ Berhasil! {item['name']} telah ditambahkan ke tas kamu.", show_alert=True)
    await cmd_shop(callback, user_service, content_service)

@router.callback_query(F.data == "shop_inventory")
async def shop_inventory(callback: types.CallbackQuery, user_service: UserService, content_service: ContentService):
    user_data = await user_service.get_user(callback.from_user.id)
    catalog = await content_service.get_shop_items()
    
    text = get_header("Inventori Personel", "🎒")
    owned = user_data.owned_items or []
    
    if not owned:
        text += "<i>Tas kamu kosong. Beli item di Bursa untuk mengisinya.</i>"
        builder = InlineKeyboardBuilder()
    else:
        text += "Pilih badge untuk digunakan (Equip) di profil utama:\n\n"
        builder = InlineKeyboardBuilder()
        for item_id in owned:
            item_info = catalog.get(item_id)
            if item_info:
                name = item_info.get("name", item_id)
                # Check if equipped
                mark = "✅ " if user_data.equipped_badge == item_id else "‣ "
                builder.button(text=f"{mark}{name}", callback_data=f"equip_{item_id}")
    
    builder.button(text="◃ KEMBALI KE BURSA", callback_data="main_shop")
    builder.adjust(1)
    
    from utils.style_utils import force_height
    text = force_height(text, 12)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("equip_"))
async def process_equip(callback: types.CallbackQuery, user_service: UserService, content_service: ContentService):
    item_id = callback.data.replace("equip_", "")
    user_data = await user_service.get_user(callback.from_user.id)
    
    if item_id not in (user_data.owned_items or []):
        await callback.answer("Kamu tidak memiliki item ini.", show_alert=True)
        return
        
    await user_service.update_user(callback.from_user.id, {"equipped_badge": item_id})
    await callback.answer("✅ Item digunakan!", show_alert=True)
    await shop_inventory(callback, user_service, content_service)
