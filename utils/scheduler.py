import asyncio
import time
import logging
from database.lfg_db import lfg_db

async def lfg_garbage_collector():
    """Background task to remove LFG sessions older than 2 hours."""
    EXPIRY_TIME_SECONDS = 7200  # 2 hours
    while True:
        try:
            current_time = time.time()
            all_sessions = await lfg_db.db.read()
            to_delete = []
            
            for session_id, data in all_sessions.items():
                timestamp = data.get("timestamp", 0)
                if current_time - timestamp > EXPIRY_TIME_SECONDS:
                    to_delete.append(session_id)
            
            for session_id in to_delete:
                await lfg_db.delete_session(session_id)
                logging.info(f"🗑️ Garbage Collector: Deleted expired LFG session {session_id}")
                
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
