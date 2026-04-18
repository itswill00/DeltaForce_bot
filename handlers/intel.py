import json
import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.style_utils import get_header, get_footer

router = Router()

# Load map data once
with open("data/maps.json", "r", encoding="utf-8") as f:
    MAP_DB = json.load(f)

@router.message(Command("map"))
@router.callback_query(F.data == "main_intel")
async def cmd_map(event: types.Message | types.CallbackQuery):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    
    # Redirect if in Group
    if message.chat.type != "private":
        bot_user = await event.bot.get_me()
        text = "🔍 <b>INTEL PETA:</b> Akses peta dan lokasi ekstraksi secara detail di chat pribadi untuk menghindari spam."
        builder = InlineKeyboardBuilder()
        builder.button(text="📍 Lihat Peta (DM)", url=f"https://t.me/{bot_user.username}?start=map")
        await message.answer(text, reply_markup=builder.as_markup())
        return

    builder = InlineKeyboardBuilder()
    maps = MAP_DB if isinstance(MAP_DB, dict) else {}
    for map_id, map_data in maps.items():
        if map_data and "name" in map_data:
            builder.button(text=f"📍 {map_data['name']}", callback_data=f"intel_map_{map_id}")
    
    builder.button(text="💎 Item Langka (Loot)", callback_data="intel_loot_list")
    builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    builder.adjust(1)
    
    text = get_header("INTEL PETA & OPERASI", "🔍")
    text += "Pilih peta untuk melihat titik ekstraksi dan lokasi berbahaya:"
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=builder.as_markup())
        await event.answer()
    else:
        await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("intel_map_"))
async def process_map_info(callback: types.CallbackQuery):
    map_id = callback.data.split("_")[2]
    map_data = MAP_DB.get(map_id)
    
    if not map_data:
        await callback.answer("Peta tidak ditemukan.")
        return
        
    text = get_header(f"PETA: {map_data.get('name', 'UNKNOWN').upper()}", "📍")
    text += (
        f"<i>{map_data.get('description', 'Data tidak tersedia.')}</i>\n\n"
        f"🔥 <b>LOKASI BAHAYA:</b>\n" + "\n".join([f"• {h}" for h in map_data.get('hotspots', [])]) + "\n\n"
        f"🚪 <b>EKSTRAKSI:</b>\n" + "\n".join([f"• {e.get('name', 'N/A')} ({e.get('type', 'Unknown')})" for e in map_data.get('extractions', [])])
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Kembali", callback_data="intel_home")
    builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@router.callback_query(F.data == "intel_home")
async def intel_home(callback: types.CallbackQuery):
    await cmd_map(callback)

@router.message(Command("loot"))
@router.callback_query(F.data == "intel_loot_list")
async def cmd_loot(event: types.Message | types.CallbackQuery):
    is_callback = isinstance(event, types.CallbackQuery)
    
    red_items = [
        "Portable Military Radar (~2.2JT)",
        "Fuel Cell (~500RB)",
        "Blade Server (~800RB)",
        "Rare Fossil (~1.5JT)",
        "Military Laptop (~400RB)"
    ]
    
    text = get_header("ITEM PRIORITAS (RED)", "💎")
    text += "Segera amankan item ini jika menemukannya:\n\n" + \
            "\n".join([f"• {item}" for item in red_items])
    text += get_footer("Nilai estimasi Auction House")
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Kembali", callback_data="intel_home")
    builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    builder.adjust(1)
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=builder.as_markup())
    else:
        await event.answer(text, reply_markup=builder.as_markup())
