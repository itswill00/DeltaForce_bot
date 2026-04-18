import asyncio
import time
import logging
from database.json_manager import db_manager

async def lfg_garbage_collector():
    """Background task to remove LFG sessions older than 2 hours."""
    EXPIRY_TIME_SECONDS = 7200  # 2 hours
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
                    logging.info(f"🗑️ Garbage Collector: Deleted expired LFG session {session_id}")
                await db_manager.save(all_data)
                
        except Exception as e:
            logging.error(f"LFG GC Error: {e}")
            
        await asyncio.sleep(600)  # Check every 10 minutes

async def auto_intel_scheduler(bot):
    """Background task to broadcast tactical intel to active groups every 6 hours."""
    from handlers.group_settings import broadcast_auto_intel
    
    # Initial delay after bot start
    await asyncio.sleep(60) 
    
    while True:
        try:
            logging.info("📡 Scheduler: Triggering Auto-Intel broadcast...")
            await broadcast_auto_intel(bot)
        except Exception as e:
            logging.error(f"Auto-Intel Scheduler Error: {e}")
            
        # Run every 6 hours
        await asyncio.sleep(21600) 
