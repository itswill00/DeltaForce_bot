import json
import random
from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.group_db import group_db
from utils.style_utils import get_header

router = Router()

@router.message(Command("settings_group"))
async def cmd_settings_group(message: types.Message):
    if message.chat.type == "private":
        await message.answer("❌ Perintah ini hanya berlaku di dalam Grup.")
        return

    # Check if user is admin
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in ["administrator", "creator"]:
        await message.answer("❌ Akses Ditolak: Hanya Admin Grup yang dapat merubah pengaturan.")
        return

    group_info = await group_db.get_group(message.chat.id)
    if not group_info:
        await group_db.register_group(message.chat.id, message.chat.title)
        group_info = await group_db.get_group(message.chat.id)
        
    s = group_info.get("settings", {})
    auto_intel = s.get("auto_intel", False)
    trivia_on = s.get("trivia_enabled", True)
    cleanup_on = s.get("auto_cleanup", True)
    
    text = get_header("PENGATURAN GRUP", "📡")
    text += (
        f"<b>Grup:</b> {message.chat.title}\n\n"
        f"1️⃣ <b>Auto-Intel:</b> {'🟢 AKTIF' if auto_intel else '🔴 MATI'}\n"
        f"2️⃣ <b>Kuis Trivia:</b> {'🟢 AKTIF' if trivia_on else '🔴 MATI'}\n"
        f"3️⃣ <b>Auto-Cleanup:</b> {'🟢 AKTIF' if cleanup_on else '🔴 MATI'}\n\n"
        "Gunakan tombol di bawah untuk mengaktifkan/menonaktifkan fitur:"
    )
    
    builder = InlineKeyboardBuilder()
    builder.button(text=f"{'🔴 Matikan' if auto_intel else '🟢 Aktifkan'} Intel", callback_data=f"grpsett_intel_{'off' if auto_intel else 'on'}")
    builder.button(text=f"{'🔴 Matikan' if trivia_on else '🟢 Aktifkan'} Trivia", callback_data=f"grpsett_trivia_{'off' if trivia_on else 'on'}")
    builder.button(text=f"{'🔴 Matikan' if cleanup_on else '🟢 Aktifkan'} Cleanup", callback_data=f"grpsett_cleanup_{'off' if cleanup_on else 'on'}")
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("grpsett_"))
async def process_group_settings(callback: types.CallbackQuery):
    # Check if user is admin
    member = await callback.message.chat.get_member(callback.from_user.id)
    if member.status not in ["administrator", "creator"]:
        await callback.answer("❌ Hanya Admin yang bisa merubah ini.", show_alert=True)
        return

    action = callback.data.split("_")[1]
    val = (callback.data.split("_")[2] == "on")
    
    label_map = {
        "intel": ("auto_intel", "Auto-Intel"),
        "trivia": ("trivia_enabled", "Trivia"),
        "cleanup": ("auto_cleanup", "Auto-Cleanup")
    }
    
    if action not in label_map: return
    
    key, label = label_map[action]
    await group_db.update_settings(callback.message.chat.id, key, val)
    
    status_str = "DIAKTIFKAN" if val else "DIMATIKAN"
    await callback.message.edit_text(
        get_header("PENGATURAN DIPERBARUI", "✅") +
        f"Fitur <b>{label}</b> telah {status_str}.\n\n"
        f"<i>Gunakan /settings_group untuk pengaturan lainnya.</i>"
    )
    await callback.answer(f"{label} {status_str}")

async def broadcast_auto_intel(bot: Bot):
    """Function to be called by a scheduler or periodic task."""
    active_groups = await group_db.get_active_intel_groups()
    if not active_groups: return
    
    # Load tactical tips (from intel handler or separate file)
    tips = [
        "Tips: Gunakan rute perbukitan di Zero Dam untuk menghindari sniper di area jembatan.",
        "Intel: Red Items 'Fuel Cell' sering ditemukan di area industri Valley.",
        "Meta: M4A1 dengan suppressor sangat direkomendasikan untuk operasi Hazard diam-diam.",
        "Strategi: Selalu sisakan 1 granat asap untuk membantu ekstraksi saat ditekan musuh.",
        "Tips: Medic adalah role tersulit tapi terpenting di Hazard Operation. Selalu prioritaskan keselamatan Medic."
    ]
    
    tip = random.choice(tips)
    text = get_header("DAILY TACTICAL INTEL", "📡") + f"<i>{tip}</i>"
    
    for gid in active_groups:
        try:
            await bot.send_message(gid, text)
        except Exception as e:
            print(f"Failed to post auto-intel to {gid}: {e}")
