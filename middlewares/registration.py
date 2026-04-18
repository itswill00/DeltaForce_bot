import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from services.user_service import UserService
from utils.auto_delete import set_auto_delete

# Commands that are allowed without registration
ALLOWED_CMDS = {"/start", "/register", "/needhelp", "/sys", "/addadmin", "/deladmin", "/force_gc", "/menu", "/dashboard", "/checkid", "/refresh"}

class RegistrationMiddleware(BaseMiddleware):
    """
    Global interceptor that blocks unregistered users from using core features.
    Updated to use Enterprise UserService.
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        user = data.get("event_from_user")
        if not user or user.is_bot:
            return await handler(event, data)

        is_msg = isinstance(event, Message)
        is_cb = isinstance(event, CallbackQuery)
        
        # 1. ALLOWED COMMANDS (Basic Access)
        if is_msg and event.text:
            cmd = event.text.split()[0].lower()
            if cmd in ALLOWED_CMDS:
                return await handler(event, data)
                
        # 2. ALLOWED CALLBACKS (Navigation & Reg Flow)
        if is_cb:
            cb_data = event.data or ""
            # Allow registration callbacks and main menu navigation
            if any(cb_data.startswith(pre) for pre in ["role_", "start_register", "main_", "intel_home"]):
                return await handler(event, data)
            if cb_data == "close_msg":
                return await handler(event, data)

        # 3. ALLOW ACTIVE FSM STATES (Crucial for IGN input)
        state = data.get("state")
        if state:
            current_state = await state.get_state()
            if current_state and "RegisterState" in current_state:
                return await handler(event, data)

        # 4. DATABASE CHECK (using injected service)
        user_service: UserService = data.get("user_service")
        user_data = await user_service.get_user(user.id)
        if user_data and user_data.ign:
            return await handler(event, data)

        # 5. BLOCK UNREGISTERED (Fallback)
        if is_msg:
            reply = await event.answer(
                "<b>🛡️ OTORISASI DIPERLUKAN</b>\n\n"
                "Silakan daftar melalui <code>/register</code> atau Menu Utama sebelum mengakses fitur ini."
            )
            asyncio.create_task(set_auto_delete(reply, event, 30))
        elif is_cb:
            await event.answer("⚠️ Silakan daftar terlebih dahulu di Menu Utama.", show_alert=True)
            
        return
