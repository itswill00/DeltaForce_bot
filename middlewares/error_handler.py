import traceback
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from utils.group_logger import send_log

class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Enterprise Error Sentinel.
    Catches all exceptions in handlers and reports them to the LOG_GROUP_ID.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            # 1. Log to console
            logging.error(f"HANDLER CRASH: {e}", exc_info=True)
            
            # 2. Prepare Diagnostic Report
            user = data.get("event_from_user")
            chat = data.get("event_chat")
            bot = data.get("bot")
            
            error_trace = traceback.format_exc()
            # Truncate traceback if too long for Telegram (max 4096 chars)
            if len(error_trace) > 3000:
                error_trace = error_trace[:3000] + "\n... [TRUNCATED]"
            
            user_info = f"{user.full_name} (<code>{user.id}</code>)" if user else "Unknown"
            chat_info = f"{chat.title} (<code>{chat.id}</code>)" if chat and chat.type != "private" else "Private Chat"
            
            trigger = "Unknown"
            if isinstance(event, Message):
                trigger = f"Command: <code>{event.text}</code>"
            elif isinstance(event, CallbackQuery):
                trigger = f"Button: <code>{event.data}</code>"

            report = (
                f"🚨 <b>SYSTEM MALFUNCTION DETECTED</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"👤 <b>User:</b> {user_info}\n"
                f"📍 <b>Chat:</b> {chat_info}\n"
                f"🎮 <b>Trigger:</b> {trigger}\n"
                f"❌ <b>Error:</b> <code>{type(e).__name__}: {str(e)}</code>\n\n"
                f"📑 <b>Traceback:</b>\n<pre>{error_trace}</pre>"
            )

            # 3. Send to Log Group
            await send_log(bot, "ERROR", report)

            # 4. Notify User politely
            error_msg = "⚠️ <b>MAAF, TERJADI KENDALA TEKNIS</b>\n\nLaporan kerusakan telah dikirim ke Pusat Komando. Masalah ini akan segera diperiksa oleh tim pengembang."
            if isinstance(event, Message):
                await event.answer(error_msg)
            elif isinstance(event, CallbackQuery):
                await event.answer("⚠️ Terjadi kesalahan sistem. Laporan telah dikirim.", show_alert=True)
            
            return None
