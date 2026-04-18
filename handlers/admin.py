from aiogram import Router, types
from aiogram.filters import Command
from database.user_db import user_db
from config import settings
from utils.group_logger import send_log

router = Router()

@router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    user_id = message.from_user.id
    is_db_admin = await user_db.is_user_admin(user_id)
    
    if user_id not in settings.admin_ids and user_id != settings.owner_id and not is_db_admin:
        await message.answer("❌ Kamu tidak memiliki izin Admin untuk menggunakan perintah ini.")
        return
        
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("Format salah! Gunakan: <code>/broadcast pesan kamu di sini</code>")
        return
        
    all_users = await user_db.get_all_users()
    success = 0
    failed = 0
    
    await message.answer(f"Mulai menyebarkan broadcast ke {len(all_users)} user yang terdaftar...")
    
    for uid_str in all_users.keys():
        try:
            await message.bot.send_message(
                chat_id=int(uid_str), 
                text=f"📢 <b>PENGUMUMAN KOMUNITAS</b>\n\n{text}"
            )
            success += 1
        except Exception:
            failed += 1
            
    await message.answer(f"<b>TRANSMISI MASSAL SELESAI</b>\nSukses terkirim: {success}\nGagal (Akses diblokir pengguna): {failed}")
    await send_log(
        message.bot, 
        "ADMIN_ACTION", 
        f"Admin ID <code>{message.from_user.id}</code> melakukan Broadcast ke {success} users.\n\nIsi: {text}"
    )
