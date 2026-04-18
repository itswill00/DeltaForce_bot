from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import UserService
from services.content_service import ContentService
from services.system_service import SystemService
from utils.style_utils import get_header, get_footer, format_field, get_divider, safe_edit_message

router = Router()

@router.message(Command("shop"))
@router.callback_query(F.data == "main_shop")
async def cmd_shop(event: types.Message | types.CallbackQuery, user_service: UserService, content_service: ContentService, system_service: SystemService):
    is_cb = isinstance(event, types.CallbackQuery)
    message = event.message if is_cb else event
    user_id = event.from_user.id
    banner = await system_service.get_banner("shop")
    
    if message.chat.type != "private":
        bot_user = await event.bot.get_me()
        text = "⌬ <b>BURSA ITEM:</b> Akses ditolak. Transaksi hanya diizinkan melalui saluran privat."
        builder = InlineKeyboardBuilder().button(text="⌬ BUKA BURSA (DM)", url=f"https://t.me/{bot_user.username}?start=shop")
        await message.answer(text, reply_markup=builder.as_markup())
        return

    user_data = await user_service.get_user(user_id)
    if not user_data or not user_data.ign:
        text = "❌ Silakan daftarkan Call-sign kamu terlebih dahulu sebelum mengakses bursa."
        builder = InlineKeyboardBuilder().button(text="◈ DAFTAR SEKARANG", callback_data="start_register")
        if is_cb: await safe_edit_message(event, text, builder.as_markup())
        else:
            from handlers.general import safe_answer_photo
            await safe_answer_photo(event, banner, text, builder.as_markup())
        return
        
    text = get_header("Bursa Item & Supply", "⌬")
    text += format_field("SALDO KREDIT", f"{user_data.balance} Koin")
    text += get_divider() + "Silakan pilih item yang tersedia:"
    
    catalog = await content_service.get_shop_items()
    builder = InlineKeyboardBuilder()
    for item_id, item in catalog.items():
        builder.button(text=f"‣ {item['name']} ({item['price']})", callback_data=f"buy_{item_id}")
    
    builder.button(text="🎒 BUKA INVENTORI", callback_data="shop_inventory")
    builder.button(text="◃ MENU UTAMA", callback_data="main_menu")
    builder.adjust(1)
    
    if is_cb: await safe_edit_message(event, text, builder.as_markup())
    else:
        from handlers.general import safe_answer_photo
        await safe_answer_photo(event, banner, text, builder.as_markup())

@router.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery, user_service: UserService, content_service: ContentService, system_service: SystemService):
    item_id = callback.data.replace("buy_", "")
    catalog = await content_service.get_shop_items()
    item = catalog.get(item_id)
    if not item: return
        
    user_data = await user_service.get_user(callback.from_user.id)
    if user_data.balance < item["price"]:
        await callback.answer(f"❌ Saldo tidak cukup! Butuh {item['price']} Koin.", show_alert=True)
        return
    if item_id in (user_data.owned_items or []):
        await callback.answer("⚠️ Sudah memiliki item ini.", show_alert=True)
        return
        
    owned = list(user_data.owned_items)
    owned.append(item_id)
    await user_service.add_balance(callback.from_user.id, -item["price"])
    await user_service.update_user(callback.from_user.id, {"owned_items": owned})
    await callback.answer(f"✅ Berhasil membeli {item['name']}!", show_alert=True)
    await cmd_shop(callback, user_service, content_service, system_service)

@router.callback_query(F.data == "shop_inventory")
async def shop_inventory(callback: types.CallbackQuery, user_service: UserService, content_service: ContentService):
    user_data = await user_service.get_user(callback.from_user.id)
    catalog = await content_service.get_shop_items()
    text = get_header("Inventori Personel", "🎒")
    owned = user_data.owned_items or []
    builder = InlineKeyboardBuilder()
    if not owned: text += "<i>Tas kamu kosong.</i>"
    else:
        text += "Pilih badge untuk digunakan (Equip):\n\n"
        for item_id in owned:
            item_info = catalog.get(item_id)
            if item_info:
                name = item_info.get("name", item_id)
                mark = "✅ " if user_data.equipped_badge == item_id else "‣ "
                builder.button(text=f"{mark}{name}", callback_data=f"equip_{item_id}")
    builder.button(text="◃ KEMBALI KE BURSA", callback_data="main_shop")
    builder.adjust(1)
    await safe_edit_message(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("equip_"))
async def process_equip(callback: types.CallbackQuery, user_service: UserService, content_service: ContentService):
    item_id = callback.data.replace("equip_", "")
    user_data = await user_service.get_user(callback.from_user.id)
    await user_service.update_user(callback.from_user.id, {"equipped_badge": item_id})
    await callback.answer("✅ Item digunakan!", show_alert=True)
    await shop_inventory(callback, user_service, content_service)
