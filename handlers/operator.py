import json
import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from views.operator_view import render_operator_list, render_operator_detail
from services.system_service import SystemService
from utils.style_utils import safe_edit_message
import asyncio

router = Router()

def get_op_data():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "operators.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return {"d-wolf": {"name": "D-Wolf", "role": "Assault", "description": "Specialist.", "active_skill": "Blaster", "passive_skill": "Slide"}}

def generate_op_menu():
    ops = get_op_data() or {}
    builder = InlineKeyboardBuilder()
    for op_id, op_info in ops.items():
        if op_info and "name" in op_info: builder.button(text=f"👤 {op_info['name']}", callback_data=f"op_{op_id}")
    builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

@router.message(Command("operator", "op"))
@router.callback_query(F.data == "main_operator")
async def cmd_operator(event: types.Message | types.CallbackQuery, system_service: SystemService):
    is_cb = isinstance(event, types.CallbackQuery)
    text = render_operator_list()
    if is_cb: await safe_edit_message(event, text, generate_op_menu())
    else:
        from handlers.general import safe_answer_photo
        banner = await system_service.get_banner("main")
        await safe_answer_photo(event, banner, text, generate_op_menu())

@router.callback_query(F.data.startswith("op_"))
async def process_op_selection(callback: types.CallbackQuery):
    op_id = callback.data.split("_")[1]
    if op_id == "back": await cmd_operator(callback, SystemService()); return
    ops = get_op_data()
    if op_id not in ops: await callback.answer("Data missing.", show_alert=True); return
    text = render_operator_detail(ops[op_id])
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ KEMBALI", callback_data="op_back")
    builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
    builder.adjust(1)
    await safe_edit_message(callback, text, builder.as_markup())
