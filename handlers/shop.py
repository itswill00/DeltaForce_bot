from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.user_service import UserService
from utils.style_utils import get_header, get_footer, format_field, get_divider

router = Router()

CATALOG = {
    "flair_recon": {"name": "Elite Recon Badge", "price": 500},
    "flair_medic": {"name": "Field Surgeon Badge", "price": 500},
    "flair_assault": {"name": "Vanguard Badge", "price": 500},
    "flair_vet": {"name": "Season 1 Veteran", "price": 2000}
}

@router.message(Command("shop"))
@router.callback_query(F.data == "main_shop")
async def cmd_shop(event: types.Message | types.CallbackQuery, user_service: UserService):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    user_id = event.from_user.id
    
    if message.chat.type != "private":
        bot_user = await event.bot.get_me()
        text = get_header("SUPPLY DROP ACCESS", "🛍️")
        text += "Unauthorized access in group channels. Open private link for secure transactions."
        builder = InlineKeyboardBuilder()
        builder.button(text="🛒 OPEN SUPPLY DROP (DM)", url=f"https://t.me/{bot_user.username}?start=shop")
        await message.answer(text, reply_markup=builder.as_markup())
        return

    user_data = await user_service.get_user(user_id)
    if not user_data or not user_data.ign:
        text = get_header("ACCESS DENIED", "❌")
        text += "Operator not recognized. Register profile to access Supply Drop."
        builder = InlineKeyboardBuilder()
        builder.button(text="🚀 INITIALIZE", callback_data="start_register")
        builder.button(text="🏠 HUB MENU", callback_data="main_menu")
        if is_callback: await event.message.edit_text(text, reply_markup=builder.as_markup())
        else: await event.answer(text, reply_markup=builder.as_markup())
        return
        
    text = get_header("SUPPLY DROP & REWARDS", "🛒")
    text += format_field("CREDITS", f"💰 {user_data.balance}", "🏦")
    text += get_divider()
    text += "Authorized items available for exchange:"
    
    builder = InlineKeyboardBuilder()
    for item_id, item in CATALOG.items():
        builder.button(text=f"🎖️ {item['name']} ({item['price']})", callback_data=f"buy_{item_id}")
    
    builder.button(text="🏠 HUB MENU", callback_data="main_menu")
    builder.adjust(1)
    
    text += "\n" + get_footer("Supply Chain v4.0")
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=builder.as_markup())
        await event.answer()
    else:
        await event.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery, user_service: UserService):
    item_id = callback.data.split("_")[1]
    item = CATALOG.get(item_id)
    
    if not item:
        await callback.answer("❌ Item designation invalid.", show_alert=True)
        return
        
    user_data = await user_service.get_user(callback.from_user.id)
    if not user_data: return
    
    if user_data.balance < item["price"]:
        await callback.answer(f"❌ Insufficient credits. Needed: {item['price']}.", show_alert=True)
        return
        
    owned_items = user_data.owned_items or []
    if item_id in owned_items:
        await callback.answer("⚠️ Item already in possession.", show_alert=True)
        return
        
    owned_items.append(item_id)
    await user_service.add_balance(callback.from_user.id, -item["price"])
    await user_service.update_user(callback.from_user.id, {"owned_items": owned_items})
    
    await callback.answer(f"✅ TRANSACTION CONFIRMED: {item['name']} acquired!", show_alert=True)
    await cmd_shop(callback, user_service)
