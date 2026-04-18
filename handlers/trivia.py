import json
import os
import random
import time
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.style_utils import get_header, get_footer, format_field, safe_edit_message
from services.user_service import UserService
from services.group_service import GroupService
from services.system_service import SystemService

router = Router()

def get_trivia_data():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "trivia.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return [{"question": "Siapa pengembang game Delta Force: Hawk Ops?", "options": ["Tencent (TiMi)", "Activision", "EA", "Ubisoft"], "answer": 0}]

@router.message(Command("trivia"))
@router.callback_query(F.data == "main_trivia")
async def cmd_trivia(event: types.Message | types.CallbackQuery, user_service: UserService, group_service: GroupService, system_service: SystemService):
    is_cb = isinstance(event, types.CallbackQuery)
    message = event.message if is_cb else event
    
    if message.chat.type != "private":
        group_info = await group_service.get_group(message.chat.id)
        if group_info and not group_info.settings.get("trivia_enabled", True):
            if is_cb: await event.answer("❌ Trivia dinonaktifkan.", show_alert=True)
            else: await message.answer("❌ Fitur Trivia dinonaktifkan oleh Admin.")
            return
            
    questions = get_trivia_data()
    q_idx = random.randint(0, len(questions) - 1)
    q = questions[q_idx]
    
    start_time = int(time.time())
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(q["options"]):
        builder.button(text=opt, callback_data=f"triv_{q_idx}_{i}_{q['answer']}_{start_time}")
    if message.chat.type == "private": builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
    builder.adjust(2)
    
    text = get_header("Simulasi Trivia", "🧠") + f"<b>SOAL:</b>\n{q['question']}\n\n<i>Personel tercepat mendapatkan koin.</i>"
    
    if is_cb: await safe_edit_message(event, text, builder.as_markup())
    else:
        from handlers.general import safe_answer_photo
        banner = await system_service.get_banner("main")
        await safe_answer_photo(event, banner, text, builder.as_markup())

@router.callback_query(F.data.startswith("triv_"))
async def process_trivia(callback: types.CallbackQuery, user_service: UserService, group_service: GroupService, system_service: SystemService):
    parts = callback.data.split("_")
    q_idx, chosen, correct, st_val = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
    delta = time.time() - st_val
    questions = get_trivia_data()
    q = questions[q_idx]
    
    if chosen == correct:
        await user_service.increment_trivia_score(callback.from_user.id, 5)
        await user_service.add_balance(callback.from_user.id, 100)
        text = get_header("Evaluasi: Tepat!", "✅") + f"<b>Q</b>: {q['question']}\n" + format_field("HASIL", "BENAR") + format_field("WAKTU", f"{delta:.1f}s") + format_field("HADIAH", "+100 Koin")
        if callback.message.chat.type != "private": await group_service.track_member(callback.message.chat.id, callback.from_user.id)
    else:
        text = get_header("Evaluasi: Salah", "❌") + f"<b>Q</b>: {q['question']}\n" + format_field("JAWABAN", q['options'][correct])
        
    builder = InlineKeyboardBuilder()
    builder.button(text="🧠 LAGI", callback_data="main_trivia")
    builder.button(text="🏠 MENU", callback_data="main_menu")
    builder.adjust(1)
    await safe_edit_message(callback, text, builder.as_markup())
    await callback.answer()
