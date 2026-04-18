import logging
from aiogram import Bot
from config import settings

async def send_log(bot: Bot, action_type: str, details: str):
    """
    Sends a formatted log message to the designated LOG_GROUP_ID.
    action_type: Brief category (e.g. "NEW_USER", "INTERAKSI_USER")
    details: Detailed description of the event.
    """
    if not settings.log_group_id:
        return
        
    emojis = {
        "NEW_USER": "👤",
        "LFG_CREATED": "🎮",
        "LFG_FULL": "🎉",
        "LFG_CLOSED": "🔒",
        "ADMIN_ACTION": "⚠️",
        "ERROR": "❌",
        "INTERAKSI_USER": "💬",
        "INTERAKSI_TOMBOL": "🔘"
    }
    
    icon = emojis.get(action_type, "ℹ️")
    text = (
        f"{icon} <b>BOT LOG: {action_type}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{details}"
    )
    
    try:
        await bot.send_message(chat_id=settings.log_group_id, text=text)
    except Exception as e:
        logging.error(f"Failed to send log to group {settings.log_group_id}: {e}")
