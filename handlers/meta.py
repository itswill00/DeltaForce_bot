import json
import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.paginator import InlineKeyboardPaginator
from utils.auto_delete import set_auto_delete
from utils.style_utils import get_header, get_footer, safe_edit_message
from services.system_service import SystemService
from services.content_service import ContentService
import asyncio

router = Router()

def get_meta_data():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "loadout.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f).get("senjata", {})
    except Exception: return {}

def get_categories():
    db = get_meta_data() or {}
    cats = set()
    for w in db.values():
        if w and "category" in w: cats.add(w["category"])
    return list(cats)

@router.message(Command("meta"))
@router.callback_query(F.data == "main_meta")
async def cmd_meta(event: types.Message | types.CallbackQuery, system_service: SystemService):
    is_cb = isinstance(event, types.CallbackQuery)
    
    categories = get_categories()
    builder = InlineKeyboardBuilder()
    for c in categories:
        builder.button(text=f"⬢ {c.upper()}", callback_data=f"meta_cat_{c}")
    builder.button(text="◃ MENU UTAMA", callback_data="main_menu")
    builder.adjust(2)
    
    text = get_header("Arsenal & Meta", "🔫") + "Pilih kategori spesialisasi untuk memuat data loadout:"
    
    if is_cb:
        await safe_edit_message(event, text, builder.as_markup())
    else:
        banner = await system_service.get_banner("main")
        from handlers.general import safe_answer_photo
        await safe_answer_photo(event, banner, text, builder.as_markup())

@router.callback_query(F.data.startswith("meta_"))
async def process_meta(callback: types.CallbackQuery, system_service: SystemService):
    action = callback.data.split("_")[1]
    param = "_".join(callback.data.split("_")[2:])
    db = get_meta_data()
    
    if action == "home":
        await cmd_meta(callback, system_service)
        return
        
    elif action == "cat":
        weapons = [(f"meta_wpn_{wid}", w['name']) for wid, w in (db or {}).items() if w and w.get("category") == param]
        paginator = InlineKeyboardPaginator(items=weapons, items_per_page=6, callback_prefix=f"meta_page_{param}_")
        builder = paginator.get_page(0)
        builder.button(text="◃ KEMBALI", callback_data="meta_home")
        builder.button(text="◃ MENU UTAMA", callback_data="main_menu")
        builder.adjust(2)
        await safe_edit_message(callback, f"⬡ <b>KATEGORI: {param.upper()}</b>\nPilih model unit untuk audit detail:", reply_markup=builder.as_markup())

    elif action == "page":
        category = callback.data.split("_")[2]
        page = int(callback.data.split("_")[3])
        weapons = [(f"meta_wpn_{wid}", w['name']) for wid, w in (db or {}).items() if w and w.get("category") == category]
        paginator = InlineKeyboardPaginator(items=weapons, items_per_page=6, callback_prefix=f"meta_page_{category}_")
        builder = paginator.get_page(page)
        builder.button(text="◃ KEMBALI", callback_data="meta_home")
        builder.button(text="◃ MENU UTAMA", callback_data="main_menu")
        builder.adjust(2)
        await safe_edit_message(callback, f"⬡ <b>KATEGORI: {category.upper()}</b> (Hal. {page+1})\nPilih model unit untuk audit detail:", reply_markup=builder.as_markup())
        
    elif action == "wpn":
        w = db.get(param)
        if not w:
            await callback.answer("Data tidak ditemukan.")
            return
        text = get_header(f"Intel Unit: {w['name'].upper()}", "🔫")
        text += f"<b>Tipe</b>: <code>{w['category']}</code>\n<b>Tier</b>: <code>{w.get('tier', 'N/A')}</code>\n\n<b>Loadout Rekomendasi:</b>\n<i>{w.get('best_loadout', 'TBA')}</i>"
        builder = InlineKeyboardBuilder()
        builder.button(text="◃ KEMBALI", callback_data=f"meta_cat_{w['category']}")
        builder.button(text="◃ MENU UTAMA", callback_data="main_menu")
        builder.adjust(1)
        await safe_edit_message(callback, text, builder.as_markup())
    
    await callback.answer()
