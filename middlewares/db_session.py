from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from database.db_session import async_session
from services.user_service import UserService
from services.lfg_service import LfgService

class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session() as session:
            # Inject session and services into handler data
            data["session"] = session
            data["user_service"] = UserService(session)
            data["lfg_service"] = LfgService(session)
            
            return await handler(event, data)
