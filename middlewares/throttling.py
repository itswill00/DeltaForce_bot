import time
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

class ThrottlingMiddleware(BaseMiddleware):
    """
    Enterprise Anti-Spam System.
    Mencegah user melakukan spam klik atau perintah dalam waktu singkat.
    Rate limit: 1 interaksi per detik.
    """
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        # Simple in-memory cache for user interaction timestamps
        # Format: {user_id: timestamp_of_last_interaction}
        self.user_timeouts = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        user = data.get("event_from_user")
        if not user or user.is_bot:
            return await handler(event, data)
            
        user_id = user.id
        current_time = time.time()
        last_interacted = self.user_timeouts.get(user_id, 0)
        
        # Check if user is interacting too fast
        if current_time - last_interacted < self.rate_limit:
            # User is spamming
            if isinstance(event, Message):
                # Optionally warn them, but usually best to just drop silently to avoid chat spam
                pass 
            elif isinstance(event, CallbackQuery):
                # Tell them via an alert that they are clicking too fast
                await event.answer("⚠️ Terlalu cepat! Tunggu sebentar...", show_alert=True)
            
            logging.warning(f"ANTI-SPAM: Blocked request from User {user_id}")
            return # Block the request entirely
            
        # Update last interacted time
        self.user_timeouts[user_id] = current_time
        
        # Prevent memory leak over time by occasionally clearing old entries (optional for larger scale)
        if len(self.user_timeouts) > 10000:
            self.user_timeouts.clear()
            
        return await handler(event, data)
