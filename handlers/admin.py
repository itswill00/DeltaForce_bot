import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError
from services.user_service import UserService
from config import settings
from utils.group_logger import send_log
from utils.style_utils import get_header, progress_bar

router = Router()

@router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message, user_service: UserService):
    user_id = message.from_user.id
    is_db_admin = await user_service.is_user_admin(user_id)
    
    if user_id not in settings.admin_ids and user_id != settings.owner_id and not is_db_admin:
        await message.answer("❌ Akses ditolak. Hanya untuk Admin.")
        return
        
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("Format salah! Gunakan: <code>/broadcast pesan kamu di sini</code>")
        return
        
    all_users = await user_service.get_all_users()
    total_users = len(all_users)
    
    if total_users == 0:
        await message.answer("Belum ada user yang terdaftar di database.")
        return

    status_msg = await message.answer(
        get_header("TRANSMISI MASSAL", "📡") +
        f"Memulai broadcast ke {total_users} operator...\n"
        f"{progress_bar(0, total_users)}"
    )
    
    success = 0
    failed = 0
    
    for i, uid_int in enumerate(all_users.keys()):
        try:
            await message.bot.send_message(
                chat_id=uid_int, 
                text=f"📢 <b>PENGUMUMAN KOMUNITAS</b>\n\n{text}"
            )
            success += 1
        except TelegramRetryAfter as e:
            # Smart delay if Telegram rate limits us
            await asyncio.sleep(e.retry_after)
            try:
                await message.bot.send_message(chat_id=uid_int, text=f"📢 <b>PENGUMUMAN KOMUNITAS</b>\n\n{text}")
                success += 1
            except:
                failed += 1
        except TelegramForbiddenError:
            # User blocked the bot
            failed += 1
        except Exception:
            failed += 1
            
        # Standard safety delay (max ~30 msgs/sec for Telegram API)
        await asyncio.sleep(0.05)
        
        # Update progress message every 50 users to avoid rate-limiting the status update
        if i > 0 and i % 50 == 0:
            try:
                await status_msg.edit_text(
                    get_header("TRANSMISI MASSAL", "📡") +
                    f"Proses berjalan: {i}/{total_users}\n"
                    f"{progress_bar(i, total_users)}"
                )
            except:
                pass
            
    # Final Report
    final_text = get_header("TRANSMISI SELESAI", "✅")
    final_text += (
        f"<b>Total Target:</b> {total_users}\n"
        f"<b>Berhasil:</b> {success}\n"
        f"<b>Gagal/Blok:</b> {failed}\n\n"
        f"{progress_bar(total_users, total_users)}"
    )
    
    await status_msg.edit_text(final_text)
    
    await send_log(
        message.bot, 
        "ADMIN_ACTION", 
        f"Admin ID <code>{message.from_user.id}</code> melakukan Broadcast.\nBerhasil: {success} | Gagal: {failed}\n\nIsi: {text}"
    )
