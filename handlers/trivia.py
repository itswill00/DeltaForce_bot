import json
import os
import random
import time
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.style_utils import get_header, get_footer
from services.user_service import UserService
from services.group_service import GroupService

router = Router()

def get_trivia_data():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "trivia.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback if file doesn't exist
        return [
            {
                "question": "Siapa pengembang game Delta Force: Hawk Ops?",
                "options": ["Tencent (TiMi)", "Activision", "EA", "Ubisoft"],
                "answer": 0
            }
        ]

@router.message(Command("trivia"))
@router.callback_query(F.data == "main_trivia")
async def cmd_trivia(event: types.Message | types.CallbackQuery, user_service: UserService, group_service: GroupService):
    is_callback = isinstance(event, types.CallbackQuery)
    message = event.message if is_callback else event
    
    # Check group settings if in group
    if message.chat.type != "private":
        group_info = await group_service.get_group(message.chat.id)
        if group_info and not group_info.settings.get("trivia_enabled", True):
            if is_callback:
                await event.answer("❌ Trivia dinonaktifkan di grup ini.", show_alert=True)
            else:
                await message.answer("❌ Fitur Trivia dinonaktifkan di grup ini oleh Admin.")
            return
            
    questions = get_trivia_data()
    if not questions:
        text = "❌ Maaf, belum ada soal trivia yang tersedia saat ini."
        if is_callback: await event.message.edit_text(text)
        else: await event.answer(text)
        return
        
    q_idx = random.randint(0, len(questions) - 1)
    q = questions[q_idx]
    
    start_time = int(time.time())
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(q["options"]):
        builder.button(text=opt, callback_data=f"triv_{q_idx}_{i}_{q['answer']}_{start_time}")
    
    if message.chat.type == "private":
        builder.button(text="🏠 Menu Utama", callback_data="main_menu")
    else:
        bot_user = await event.bot.get_me()
        builder.button(text="👤 Profil (DM)", url=f"https://t.me/{bot_user.username}?start=profile")
        
    builder.adjust(2)
    
    text = get_header("SIMULASI TRIVIA", "🧠")
    text += f"<b>SOAL:</b>\n{q['question']}\n\n"
    text += "<i>Hanya personel tercepat yang mendapat hadiah!</i>"
    
    if is_callback:
        await event.message.edit_text(text, reply_markup=builder.as_markup())
        await event.answer()
    else:
        await event.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("triv_"))
async def process_trivia(callback: types.CallbackQuery, user_service: UserService, group_service: GroupService):
    parts = callback.data.split("_")
    if len(parts) == 2 and parts[1] == "done":
        await callback.answer("Simulasi ini telah diselesaikan.", show_alert=True)
        return
        
    q_idx = int(parts[1])
    chosen = int(parts[2])
    correct = int(parts[3])
    start_time_val = int(parts[4]) if len(parts) > 4 else None
    
    delta = time.time() - start_time_val if start_time_val else 0
    time_str = f" dalam {delta:.1f} detik" if delta > 0 else ""
    
    questions = get_trivia_data()
    q = questions[q_idx]
    
    user_name = callback.from_user.first_name
    
    if chosen == correct:
        await user_service.increment_trivia_score(callback.from_user.id, 5)
        await user_service.add_balance(callback.from_user.id, 100)
        
        text = get_header("EVALUASI: TEPAT!", "✅")
        text += (
            f"<b>SOAL:</b> {q['question']}\n\n"
            f"<b>JAWABAN:</b> {q['options'][correct]}\n"
            f"<b>JUARA:</b> {user_name}{time_str} (+10 XP, +100 Coins)"
        )
        
        # Track group member
        if callback.message.chat.type != "private":
            await group_service.track_member(callback.message.chat.id, callback.from_user.id)
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🧠 Main Lagi", callback_data="main_trivia")
        if callback.message.chat.type == "private":
            builder.button(text="🏠 Menu Utama", callback_data="main_menu")
        else:
            bot_user = await callback.bot.get_me()
            builder.button(text="👤 Profil (DM)", url=f"https://t.me/{bot_user.username}?start=profile")
        builder.adjust(1)
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        await callback.answer("Tepat! +100 Coins.")
    else:
        text = get_header("EVALUASI: MELESET", "❌")
        text += (
            f"<b>SOAL:</b> {q['question']}\n\n"
            f"<b>HASIL:</b> {user_name} memilih salah.\n"
            f"<b>KUNCI JAWABAN:</b> {q['options'][correct]}"
        )
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🧠 Coba Lagi", callback_data="main_trivia")
        builder.button(text="🏠 Menu Utama", callback_data="main_menu")
        builder.adjust(1)
        
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        await callback.answer("Akurasi: 0%", show_alert=True)
