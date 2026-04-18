import asyncio
import time
import logging
import os
from aiogram import Bot
from aiogram.types import FSInputFile
from database.json_manager import db_manager
from config import settings

async def lfg_garbage_collector():
    """Background task to remove LFG sessions older than 2 hours."""
    EXPIRY_TIME_SECONDS = 7200
    while True:
        try:
            current_time = time.time()
            all_data = await db_manager.get_all()
            all_sessions = all_data.get("lfg", {})
            to_delete = []
            
            for session_id, data in list(all_sessions.items()):
                timestamp = data.get("timestamp", 0)
                if timestamp and current_time - timestamp > EXPIRY_TIME_SECONDS:
                    to_delete.append(session_id)
            
            if to_delete:
                for session_id in to_delete:
                    if session_id in all_data["lfg"]:
                        del all_data["lfg"][session_id]
                await db_manager.save(all_data)
                logging.info(f"🗑️ GC: Deleted {len(to_delete)} expired sessions.")
                
        except Exception as e:
            logging.error(f"LFG GC Error: {e}")
            
        await asyncio.sleep(600)

async def auto_intel_scheduler(bot: Bot):
    """Background task to broadcast tactical intel every 6 hours."""
    from handlers.group_settings import broadcast_auto_intel
    await asyncio.sleep(60) 
    while True:
        try:
            await broadcast_auto_intel(bot)
        except Exception as e:
            logging.error(f"Auto-Intel Error: {e}")
        await asyncio.sleep(21600) 

async def database_backup_scheduler(bot: Bot):
    """
    CRITICAL: Enterprise Data Protection.
    Sends a backup of localdb.json to the LOG_GROUP_ID every 2 hours.
    """
    if not settings.log_group_id:
        logging.warning("⚠️ Backup Scheduler: LOG_GROUP_ID not set. Backups disabled.")
        return

    # Initial delay to let bot stabilize
    await asyncio.sleep(30)
    
    while True:
        try:
            if os.path.exists(settings.local_db_path):
                backup_file = FSInputFile(settings.local_db_path, filename=f"backup_{int(time.time())}.json")
                await bot.send_document(
                    chat_id=settings.log_group_id,
                    document=backup_file,
                    caption=(
                        "◈ <b>DATA BACKUP RECOVERY</b> ◈\n\n"
                        f"Target: <code>{settings.local_db_path}</code>\n"
                        f"Status: SUCCESS\n"
                        f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        "<i>Simpan file ini untuk pemulihan jika VPS mati mendadak.</i>"
                    )
                )
                logging.info("💾 Database backup sent to Log Group.")
            else:
                logging.error("❌ Backup Failure: Database file not found.")
        except Exception as e:
            logging.error(f"Backup Scheduler Error: {e}")
            
        # Run every 2 hours
        await asyncio.sleep(7200)
