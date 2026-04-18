from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.json_manager import db_manager
from services.user_service import UserService
from services.lfg_service import LfgService

class DbSessionMiddleware(BaseMiddleware):
    """Provides JSON Services to handlers. Replaces SQLAlchemy session middleware."""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # We inject the JSON services
        # No 'session' object is needed for JSON layers, but we keep the structure 
        # consistent with the previous version to minimize handler changes.
        data["user_service"] = UserService(db_manager)
        data["lfg_service"] = LfgService(db_manager)
        
        return await handler(event, data)
