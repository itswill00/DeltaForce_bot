import logging
from aiogram import Bot
from config import settings
import time

async def send_log(bot: Bot, action_type: str, details: str):
    """
    Enterprise Logger: Mirrors all events to both Telegram Log Group and VPS Terminal.
    """
    # 1. Terminal Logging (Local Mirror)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    # Strip HTML tags for clean terminal output
    clean_details = details.replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", "").replace("<pre>", "").replace("</pre>", "")
    print(f"[{timestamp}] [AUDIT] {action_type}: {clean_details}")
    
    # Standard python logging integration
    logging.info(f"AUDIT_{action_type}: {clean_details}")

    # 2. Telegram Logging (Remote Audit)
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
        # Use attempt-based logic to avoid blocking if Telegram API is slow
        await bot.send_message(chat_id=settings.log_group_id, text=text)
    except Exception as e:
        logging.error(f"Failed to mirror log to Telegram: {e}")
