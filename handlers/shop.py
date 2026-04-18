from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.user_db import user_db
from utils.style_utils import get_header, get_footer

router = Router()

CATALOG = {
    "flair_recon": {"name": "Elite Recon Badge", "price": 500, "description": "Tanda pangkat pengintai elit."},
    "flair_medic": {"name": "Field Surgeon Badge", "price": 500, "description": "Tanda pangkat medis lapangan."},
    "flair_assault": {"name": "Vanguard Badge", "price": 500, "description": "Tanda pangkat pasukan barisan depan."},
    "flair_vet": {"name": "Season 1 Veteran", "price": 2000, "description": "Gelar prestisius veteran musim pertama."}
}

@router.message(Command("shop"))
@router.callback_query(F.data == "main_shop")
async def cmd_shop(event: types.Message | types.CallbackQuery):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    user_id = event.from_user.id
    
    # Redirect if in Group
    if message.chat.type != "private":
        bot_user = await event.bot.get_me()
        text = "🛍️ <b>BURSA PANGKAT:</b> Silakan buka toko di chat pribadi untuk melihat saldo dan melakukan transaksi."
        builder = InlineKeyboardBuilder()
        builder.button(text="🛒 Buka Toko (DM)", url=f"https://t.me/{bot_user.username}?start=shop")
        await message.answer(text, reply_markup=builder.as_markup())
        return

    user_data = await user_db.get_user(user_id)
    if not user_data or "ign" not in user_data:
        text = "❌ Profil tidak ditemukan. Silakan daftar terlebih dahulu sebelum berbelanja."
        builder = InlineKeyboardBuilder()
        builder.button(text="🚀 Daftar Sekarang", callback_data="start_register")
        builder.button(text="🏠 Menu Utama", callback_data="main_menu")
        if is_callback: await event.message.edit_text(text, reply_markup=builder.as_markup())
        else: await event.answer(text, reply_markup=builder.as_markup())
        return
        
    balance = user_data.get("balance", 0)
    
    text = get_header("BURSA PANGKAT & ITEM", "🛒")
    text += f"💰 <b>SALDO:</b> {balance} Coins\n\n"
    text += "Gunakan koin Anda untuk membeli tanda pangkat eksklusif:"
    
    builder = InlineKeyboardBuilder()
    for item_id, item in CATALOG.items():
        builder.button(text=f"🎖️ {item['name']} ({item['price']})", callback_data=f"buy_{item_id}")
    
    builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    builder.adjust(1)
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=builder.as_markup())
        await event.answer()
    else:
        await event.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery):
    item_id = callback.data.split("_")[1]
    item = CATALOG.get(item_id)
    
    if not item:
        await callback.answer("❌ Item tidak tersedia atau kadaluarsa.", show_alert=True)
        return
        
    user_data = await user_db.get_user(callback.from_user.id)
    if not user_data:
        await callback.answer("❌ Profil tidak ditemukan. Silakan /register.", show_alert=True)
        return
        
    balance = user_data.get("balance", 0)
    
    if balance < item["price"]:
        await callback.answer(f"❌ Saldo tidak cukup! Butuh {item['price']}, Saldo Anda {balance}.", show_alert=True)
        return
        
    # Grant item (add to a list in user_db)
    owned_items = user_data.get("owned_items", [])
    if item_id in owned_items:
        await callback.answer("⚠️ Anda sudah memiliki tanda pangkat ini.", show_alert=True)
        return
        
    owned_items.append(item_id)
    await user_db.add_balance(callback.from_user.id, -item["price"])
    await user_db.update_user(callback.from_user.id, {"owned_items": owned_items})
    
    await callback.answer(f"✅ Transaksi Berhasil: {item['name']} diperoleh!", show_alert=True)
    
    # Update shop view
    new_balance = balance - item["price"]
    text = get_header("BURSA PANGKAT & ITEM", "🛒")
    text += f"💰 <b>SALDO:</b> {new_balance} Coins\n\n"
    text += "Transaksi berhasil dikonfirmasi."
    
    builder = InlineKeyboardBuilder()
    for i_id, i in CATALOG.items():
        builder.button(text=f"🎖️ {i['name']} ({i['price']})", callback_data=f"buy_{i_id}")
    builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
