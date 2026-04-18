import json
import os
import random
import time
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.style_utils import get_header, get_footer, format_field
from services.user_service import UserService
from services.group_service import GroupService

router = Router()

def get_trivia_data():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "trivia.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return [{"question": "Siapa pengembang game Delta Force: Hawk Ops?", "options": ["Tencent (TiMi)", "Activision", "EA", "Ubisoft"], "answer": 0}]

@router.message(Command("trivia"))
@router.callback_query(F.data == "main_trivia")
async def cmd_trivia(event: types.Message | types.CallbackQuery, user_service: UserService, group_service: GroupService):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    
    if message.chat.type != "private":
        group_info = await group_service.get_group(message.chat.id)
        if group_info and not group_info.settings.get("trivia_enabled", True):
            if is_callback: await event.answer("❌ Trivia dinonaktifkan di grup ini.", show_alert=True)
            else: await message.answer("❌ Fitur Trivia dinonaktifkan di grup ini oleh Admin.")
            return
            
    questions = get_trivia_data()
    q_idx = random.randint(0, len(questions) - 1)
    q = questions[q_idx]
    
    start_time = int(time.time())
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(q["options"]):
        builder.button(text=opt, callback_data=f"triv_{q_idx}_{i}_{q['answer']}_{start_time}")
    
    if message.chat.type == "private":
        builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
    else:
        bot_user = await event.bot.get_me()
        builder.button(text="👤 PROFIL (DM)", url=f"https://t.me/{bot_user.username}?start=profile")
    builder.adjust(2)
    
    text = get_header("Simulasi Trivia", "🧠")
    text += f"<b>SOAL:</b>\n{q['question']}\n\n"
    text += "<i>Personel tercepat akan mendapatkan koin.</i>"
    
    if is_callback: await event.message.edit_text(text, reply_markup=builder.as_markup())
    else: await event.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("triv_"))
async def process_trivia(callback: types.CallbackQuery, user_service: UserService, group_service: GroupService):
    parts = callback.data.split("_")
    if len(parts) == 2 and parts[1] == "done":
        await callback.answer("Simulasi telah selesai.", show_alert=True)
        return
        
    q_idx, chosen, correct, st_val = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
    delta = time.time() - st_val
    questions = get_trivia_data()
    q = questions[q_idx]
    
    if chosen == correct:
        await user_service.increment_trivia_score(callback.from_user.id, 5)
        await user_service.add_balance(callback.from_user.id, 100)
        
        text = get_header("Evaluasi: Tepat!", "✅")
        text += f"<b>Q</b>: {q['question']}\n"
        text += format_field("HASIL", "BENAR")
        text += format_field("WAKTU", f"{delta:.1f} detik")
        text += format_field("HADIAH", "+100 Koin")
        
        if callback.message.chat.type != "private":
            await group_service.track_member(callback.message.chat.id, callback.from_user.id)
            
        builder = InlineKeyboardBuilder()
        builder.button(text="🧠 MAIN LAGI", callback_data="main_trivia")
        builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
        builder.adjust(1)
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        await callback.answer("Tepat! Koin telah ditambahkan.")
    else:
        text = get_header("Evaluasi: Salah", "❌")
        text += f"<b>Q</b>: {q['question']}\n"
        text += format_field("JAWABAN", q['options'][correct])
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🧠 COBA LAGI", callback_data="main_trivia")
        builder.button(text="🏠 MENU UTAMA", callback_data="main_menu")
        builder.adjust(1)
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        await callback.answer("Akurasi: 0%", show_alert=True)
