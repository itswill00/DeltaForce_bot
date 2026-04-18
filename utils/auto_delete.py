import asyncio
import logging
from aiogram.types import Message
from config import settings

async def set_auto_delete(bot_msg: Message, user_msg: Message = None, delay: int = None):
    """
    Sleeps for `delay` seconds (default from settings), then attempts to delete both the bot's response 
    and the user's triggering command message.
    """
    if delay is None:
        delay = settings.auto_delete_delay
    await asyncio.sleep(delay)
    
    if bot_msg:
        try:
            await bot_msg.delete()
        except Exception as e:
            logging.debug(f"Failed to delete bot message: {e}")
            
    if user_msg:
        try:
            await user_msg.delete()
        except Exception as e:
            logging.debug(f"Failed to delete user message: {e}")
