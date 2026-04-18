import json
import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from views.operator_view import render_operator_list, render_operator_detail
import asyncio

router = Router()

def get_op_data():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "operators.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "d-wolf": {
                "name": "D-Wolf (Kai Silva)",
                "role": "Assault",
                "description": "Tactical specialist with exoskeleton enhancements for mobility and aggression.",
                "active_skill": "Exoskeleton Overdrive",
                "passive_skill": "Combat Agility"
            }
        }

def generate_op_menu():
    ops = get_op_data() or {}
    builder = InlineKeyboardBuilder()
    for op_id, op_info in ops.items():
        if op_info and "name" in op_info:
            builder.button(text=f"👤 {op_info['name']}", callback_data=f"op_{op_id}")
    builder.button(text="🏠 HUB MENU", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

@router.message(Command("operator", "op"))
@router.callback_query(F.data == "main_operator")
async def cmd_operator(event: types.Message | types.CallbackQuery):
    is_callback = isinstance(event, types.CallbackQuery)
    text = render_operator_list()
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=generate_op_menu())
        await event.answer()
    else:
        await event.answer(text, reply_markup=generate_op_menu())

@router.callback_query(F.data.startswith("op_"))
async def process_op_selection(callback: types.CallbackQuery):
    op_id = callback.data.split("_")[1]
    
    if op_id == "back":
        await cmd_operator(callback)
        return
        
    ops = get_op_data()
    if op_id not in ops:
        await callback.answer("Dossier encrypted or missing.", show_alert=True)
        return
        
    op = ops[op_id]
    text = render_operator_detail(op)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ BACK TO LIST", callback_data="op_back")
    builder.button(text="🏠 HUB MENU", callback_data="main_menu")
    builder.adjust(1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()
