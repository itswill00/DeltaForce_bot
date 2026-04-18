from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.json_manager import db_manager
from services.user_service import UserService
from services.lfg_service import LfgService
from services.group_service import GroupService
from services.content_service import ContentService
from services.security_service import SecurityService
from services.system_service import SystemService

class DbSessionMiddleware(BaseMiddleware):
    """Provides JSON Services to handlers. Injects all enterprise services."""
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Inject all required services into the data dictionary
        data["user_service"] = UserService(db_manager)
        data["lfg_service"] = LfgService(db_manager)
        data["group_service"] = GroupService(db_manager)
        data["content_service"] = ContentService(db_manager)
        data["security_service"] = SecurityService(db_manager)
        data["system_service"] = SystemService(db_manager)
        
        return await handler(event, data)
