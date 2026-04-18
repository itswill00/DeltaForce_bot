import json
import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.style_utils import get_header, get_footer
import asyncio
from utils.auto_delete import set_auto_delete

router = Router()

def get_op_data():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "operators.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def generate_op_menu():
    ops = get_op_data() or {}
    builder = InlineKeyboardBuilder()
    for op_id, op_info in ops.items():
        if op_info and "name" in op_info:
            builder.button(text=f"👤 {op_info['name']}", callback_data=f"op_{op_id}")
    builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

@router.message(Command("operator", "op"))
@router.callback_query(F.data == "main_operator")
async def cmd_operator(event: types.Message | types.CallbackQuery):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    
    text = get_header("DATABASE OPERATOR", "🚑")
    text += "Pilih operator untuk melihat spesialisasi dan kemampuan taktisnya:"
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=generate_op_menu())
        await event.answer()
    else:
        await message.answer(text, reply_markup=generate_op_menu())

@router.callback_query(F.data.startswith("op_"))
async def process_op_selection(callback: types.CallbackQuery):
    op_id = callback.data.split("_")[1]
    
    if op_id == "back":
        await cmd_operator(callback)
        return
        
    ops = get_op_data()
    if op_id not in ops:
        await callback.answer("Data operator terenkripsi/hilang.")
        return
        
    op = ops[op_id]
    
    role_map = {
        "Assault": "[ Assault/Pendobrak ]",
        "Recon": "[ Recon/Pengintai ]",
        "Medic": "[ Medic/Medis ]",
        "Engineer": "[ Engineer/Teknisi ]"
    }
    icon = role_map.get(op.get("role"), "Operator")
    
    text = get_header(f"OPERATOR: {op.get('name', 'N/A').upper()}", "👤")
    text += (
        f"<b>ROLE:</b> {icon}\n"
        f"<i>\"{op.get('description', 'Data tidak tersedia.')}\"</i>\n\n"
        f"<b>AKTIF:</b> {op.get('active_skill', 'N/A')}\n"
        f"<b>PASIF:</b> {op.get('passive_skill', 'N/A')}"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Kembali", callback_data="op_back")
    builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
