import json
import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.paginator import InlineKeyboardPaginator
from utils.auto_delete import set_auto_delete
from utils.style_utils import get_header, get_footer
import asyncio

router = Router()

def get_meta_data():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "loadout.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f).get("senjata", {})
    except Exception:
        return {}

def get_categories():
    db = get_meta_data() or {}
    cats = set()
    for w in db.values():
        if w and "category" in w:
            cats.add(w["category"])
    return list(cats)

@router.message(Command("meta"))
@router.callback_query(F.data == "main_meta")
async def cmd_meta(event: types.Message | types.CallbackQuery):
    is_callback = isinstance(event, types.CallbackQuery)
    
    categories = get_categories()
    builder = InlineKeyboardBuilder()
    for c in categories:
        builder.button(text=f"📂 {c}", callback_data=f"meta_cat_{c}")
    builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
    builder.adjust(2)
    
    text = get_header("INFO SENJATA & META", "🔫")
    text += "Pilih kategori senjata untuk melihat detail loadout dan tier list:"
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=builder.as_markup())
        await event.answer()
        msg = event.message
    else:
        msg = await event.answer(text, reply_markup=builder.as_markup())
    
    asyncio.create_task(set_auto_delete(msg, event if not is_callback else event.message, 120))

@router.callback_query(F.data.startswith("meta_"))
async def process_meta(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    param = "_".join(callback.data.split("_")[2:]) # Handles spaces in categories
    db = get_meta_data()
    
    if action == "home":
        await cmd_meta(callback)
        return
        
    elif action == "cat":
        # Filter weapons in this category (None-safe)
        weapons = [(f"meta_wpn_{wid}", w['name']) for wid, w in (db or {}).items() if w and w.get("category") == param]
        
        paginator = InlineKeyboardPaginator(
            items=weapons, 
            items_per_page=6, 
            callback_prefix=f"meta_page_{param}_"
        )
        builder = paginator.get_page(0)
        builder.button(text="◃ KEMBALI", callback_data="meta_home")
        builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
        builder.adjust(2)
        
        await callback.message.edit_text(
            f"📂 <b>KATEGORI: {param.upper()}</b>\n\nPilih model senjata:",
            reply_markup=builder.as_markup()
        )

    elif action == "page":
        # Handle weapon list pagination
        category = callback.data.split("_")[2]
        page = int(callback.data.split("_")[3])
        
        weapons = [(f"meta_wpn_{wid}", w['name']) for wid, w in (db or {}).items() if w and w.get("category") == category]
        
        paginator = InlineKeyboardPaginator(
            items=weapons, 
            items_per_page=6, 
            callback_prefix=f"meta_page_{category}_"
        )
        builder = paginator.get_page(page)
        builder.button(text="◃ KEMBALI", callback_data="meta_home")
        builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
        builder.adjust(2)
        
        await callback.message.edit_text(
            f"📂 <b>KATEGORI: {category.upper()}</b> (Hal. {page+1})\n\nPilih model senjata:",
            reply_markup=builder.as_markup()
        )
        
    elif action == "wpn":
        w = db.get(param)
        if not w:
            await callback.answer("Data senjata terenkripsi/tidak ditemukan.")
            return
            
        text = get_header(f"INTEL: {w['name'].upper()}", "🔫")
        text += (
            f"<b>KATEGORI:</b> {w['category']}\n"
            f"<b>TIER:</b> {w.get('tier', 'Unknown')}\n\n"
            f"<b>LOADOUT REKOMENDASI:</b>\n<i>{w.get('best_loadout', 'TBA')}</i>"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="◃ KEMBALI", callback_data=f"meta_cat_{w['category']}")
        builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
        builder.adjust(1)
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())

