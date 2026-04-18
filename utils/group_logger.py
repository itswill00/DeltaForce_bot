import logging
from aiogram import Bot
from config import settings

async def send_log(bot: Bot, action_type: str, details: str):
    """
    Sends a formatted log message to the designated LOG_GROUP_ID.
    action_type: Brief category (e.g. "NEW_USER", "LFG_CREATED", "ADMIN_ACTION")
    details: Detailed description of the event.
    """
    if settings.log_group_id == 0:
        logging.info(f"Log Group ID not set. Dropping log: [{action_type}] {details}")
        return
        
    emojis = {
        "NEW_USER": "👤",
        "LFG_CREATED": "🎮",
        "LFG_FULL": "🎉",
        "LFG_CLOSED": "🔒",
        "ADMIN_ACTION": "⚠️",
        "ERROR": "❌"
    }
    
    icon = emojis.get(action_type, "ℹ️")
    text = (
        f"{icon} <b>BOT LOG: {action_type}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{details}"
    )
    
    # Retry logic: attempt to send the log up to 2 times
    for attempt in range(2):
        try:
            await bot.send_message(chat_id=settings.log_group_id, text=text)
            break
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed to send log to group {settings.log_group_id}: {e}")
            if attempt == 1:
                # All attempts failed
                raise
