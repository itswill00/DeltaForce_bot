import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from services.user_service import UserService
from utils.auto_delete import set_auto_delete

from services.system_service import SystemService
from config import settings

# Core whitelisted commands
ALLOWED_CMDS = {"/start", "/register", "/needhelp", "/sys", "/addadmin", "/deladmin", "/force_gc", "/menu", "/dashboard", "/refresh"}

class RegistrationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        user = data.get("event_from_user")
        if not user or user.is_bot:
            return await handler(event, data)

        # 1. Global Maintenance Check (Bypass for Owner)
        if int(user.id) != int(settings.owner_id):
            sys_service = SystemService()
            sys_settings = await sys_service.get_settings()
            if sys_settings.get("maintenance", False):
                if isinstance(event, Message):
                    await event.answer("◈ <b>MAINTENANCE MODE</b>\n\nSistem sedang dalam pemeliharaan teknis untuk peningkatan performa. Silakan coba beberapa saat lagi.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Sistem dalam pemeliharaan.", show_alert=True)
                return

        is_msg = isinstance(event, Message)
        is_cb = isinstance(event, CallbackQuery)
        
        # 1. Improved Command Parsing (Handles @BotName)
        if is_msg and event.text and event.text.startswith("/"):
            cmd = event.text.split()[0].split("@")[0].lower()
            if cmd in ALLOWED_CMDS:
                return await handler(event, data)
                
        # 2. Whitelisted Callbacks
        if is_cb:
            cb_data = event.data or ""
            if any(cb_data.startswith(pre) for pre in ["role_", "start_register", "main_", "intel_home", "close_msg", "admin_"]):
                return await handler(event, data)

        # 3. State-based Bypass
        state = data.get("state")
        if state:
            current_state = await state.get_state()
            if current_state and "RegisterState" in current_state:
                return await handler(event, data)

        # 4. Auth Check
        user_service: UserService = data.get("user_service")
        user_data = await user_service.get_user(user.id)
        if user_data and user_data.ign:
            return await handler(event, data)

        # 5. Restriction Alert
        if is_msg:
            reply = await event.answer(
                "<b>🛡️ OTORISASI DIPERLUKAN</b>\n\n"
                "Silakan daftar melalui <code>/register</code> atau Menu Utama sebelum mengakses fitur ini."
            )
            asyncio.create_task(set_auto_delete(reply, event, 30))
        elif is_cb:
            await event.answer("⚠️ Silakan daftar terlebih dahulu di Menu Utama.", show_alert=True)
            
        return
