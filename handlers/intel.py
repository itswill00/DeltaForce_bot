import json
import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.style_utils import get_header, get_footer, safe_edit_message
from services.system_service import SystemService
from services.content_service import ContentService

router = Router()

@router.message(Command("intel", "map"))
@router.callback_query(F.data == "main_intel")
@router.callback_query(F.data == "intel_home")
async def cmd_intel(event: types.Message | types.CallbackQuery, content_service: ContentService, system_service: SystemService):
    is_cb = isinstance(event, types.CallbackQuery)
    maps = await content_service.get_maps()
    banner = await system_service.get_banner("intel")
    
    builder = InlineKeyboardBuilder()
    for map_id, map_data in maps.items():
        builder.button(text=f"📍 {map_data.get('name', map_id)}", callback_data=f"intel_map_{map_id}")
    builder.button(text="⌬ ITEM LANGKA", callback_data="intel_loot_list")
    builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
    builder.adjust(1)
    
    text = get_header("INTEL PETA & OPERASI", "🔍") + "Pilih sektor operasi untuk melihat detail ekstraksi:"
    if is_cb: await safe_edit_message(event, text, builder.as_markup())
    else:
        from handlers.general import safe_answer_photo
        await safe_answer_photo(event, banner, text, builder.as_markup())

@router.callback_query(F.data.startswith("intel_map_"))
async def process_map_info(callback: types.CallbackQuery, content_service: ContentService):
    map_id = callback.data.replace("intel_map_", "")
    maps = await content_service.get_maps()
    map_data = maps.get(map_id)
    if not map_data: await callback.answer("Peta tidak ditemukan.", show_alert=True); return
    
    text = get_header(f"INTEL: {map_data['name'].upper()}", "📍")
    text += f"<i>{map_data.get('description', '')}</i>\n\n<b>🔥 LOKASI BAHAYA:</b>\n" + "\n".join([f"• {h}" for h in map_data.get('hotspots', [])])
    
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ KEMBALI", callback_data="intel_home")
    builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
    builder.adjust(1)
    await safe_edit_message(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "intel_loot_list")
async def process_loot_list(callback: types.CallbackQuery):
    text = get_header("DATABASE ITEM LANGKA", "⌬") + "Informasi item bernilai tinggi sedang dienkripsi...\n\n<i>Cek kembali nanti untuk update rute looting.</i>"
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ KEMBALI", callback_data="intel_home")
    builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
    builder.adjust(1)
    await safe_edit_message(callback, text, builder.as_markup())
    await callback.answer()
