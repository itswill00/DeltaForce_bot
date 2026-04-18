import asyncio
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from utils.group_logger import send_log

class EventLoggerMiddleware(BaseMiddleware):
    """
    Enterprise Event Auditor - Optimized for Speed.
    Logs interactions in the background to prevent blocking user response.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # 1. Process the handler IMMEDIATELY
        response = await handler(event, data)
        
        user = data.get("event_from_user")
        if not user or user.is_bot:
            return response

        bot = data.get("bot")
        chat = data.get("event_chat")
        
        # 2. Log in the background (Non-blocking)
        if isinstance(event, Message) and event.text:
            chat_info = f"<b>Grup:</b> {chat.title}" if chat.type != "private" else "<b>Private Chat</b>"
            log_text = (
                f"👤 <b>User:</b> {user.full_name} (<code>{user.id}</code>)\n"
                f"📍 <b>Sektor:</b> {chat_info}\n"
                f"💬 <b>Pesan:</b> <code>{event.text}</code>"
            )
            # Create background task so we don't wait for the network request
            asyncio.create_task(send_log(bot, "INTERAKSI_USER", log_text))

        elif isinstance(event, CallbackQuery):
            chat_info = f"<b>Grup:</b> {chat.title}" if chat.type != "private" else "<b>Private Chat</b>"
            log_text = (
                f"👤 <b>User:</b> {user.full_name} (<code>{user.id}</code>)\n"
                f"📍 <b>Sektor:</b> {chat_info}\n"
                f"🔘 <b>Tombol:</b> <code>{event.data}</code>"
            )
            # Non-blocking background log
            asyncio.create_task(send_log(bot, "INTERAKSI_TOMBOL", log_text))

        return response
