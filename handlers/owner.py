from aiogram import Router, types
from aiogram.filters import Command
from config import settings
from services.user_service import UserService
from services.lfg_service import LfgService
from utils.group_logger import send_log
from utils.style_utils import get_header, get_footer
import psutil
import time
import os
import sys
import asyncio

router = Router()

def is_owner(user_id: int) -> bool:
    return user_id == settings.owner_id

@router.message(Command("sys"))
async def cmd_sys(message: types.Message, user_service: UserService, lfg_service: LfgService):
    if not is_owner(message.from_user.id): return
        
    user_count = await user_service.get_user_count()
    all_data = await lfg_service.db.get_all()
    active_lfg_count = len([k for k,v in all_data.get("lfg", {}).items() if v.get("status") == "open"])
    
    ram = psutil.virtual_memory()
    uptime = int(time.time() - psutil.boot_time())
    
    text = get_header("Sistem Kontrol Pusat", "⚙️")
    text += f"<b>RAM Usage</b>: {ram.percent}%\n"
    text += f"<b>Uptime</b>: {uptime}s\n"
    text += f"<b>Total User</b>: {user_count}\n"
    text += f"<b>LFG Aktif</b>: {active_lfg_count}\n"
    
    builder = InlineKeyboardBuilder()
    builder.button(text="◃ TUTUP", callback_data="close_msg")
    
    await message.answer(text, reply_markup=builder.as_markup())

@router.message(Command("refresh"))
async def cmd_refresh(message: types.Message):
    """
    Owner Feature: Pulls latest code and restarts the process.
    Usage: /refresh
    """
    if not is_owner(message.from_user.id):
        return

    status_msg = await message.answer("◈ <b>Memulai Prosedur Update...</b>\n\n⬢ Menarik kode dari GitHub...")
    
    try:
        # 1. Execute Git Pull
        process = await asyncio.create_subprocess_shell(
            "git pull origin main",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        output = stdout.decode().strip()
        
        if "Already up to date" in output:
            await status_msg.edit_text(
                get_header("Update Dibatalkan", "◈") +
                "Sistem sudah menggunakan versi terbaru di GitHub.\n\n" +
                f"<code>{output}</code>"
            )
            return

        # 2. Notify Success and Restart
        await status_msg.edit_text(
            get_header("Update Berhasil", "✅") +
            "Kode terbaru berhasil ditarik.\n\n" +
            f"<code>{output}</code>\n\n" +
            "<b>Sistem akan segera restart...</b>"
        )
        
        await send_log(message.bot, "ADMIN_ACTION", f"Owner memicu /refresh. Sistem melakukan pull dan restart.")
        
        # Give a small delay to ensure message is sent
        await asyncio.sleep(2)
        
        # 3. SELF-RESTART (Process Replacement with Handshake)
        # We pass --restart [chat_id] [message_id] to the new process
        os.execv(sys.executable, [sys.executable, sys.argv[0], "--restart", str(message.chat.id), str(status_msg.message_id)])
        
    except Exception as e:
        await status_msg.edit_text(f"❌ <b>Update Gagal:</b>\n<code>{str(e)}</code>")

@router.message(Command("addadmin"))
async def cmd_addadmin(message: types.Message, user_service: UserService):
    if not is_owner(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Format: <code>/addadmin ID_USER</code>")
        return
    target_id = int(args[1])
    await user_service.set_admin_status(target_id, True)
    await message.answer(f"Status Admin diberikan kepada ID <code>{target_id}</code>.")

@router.message(Command("deladmin"))
async def cmd_deladmin(message: types.Message, user_service: UserService):
    if not is_owner(message.from_user.id): return
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Format: <code>/deladmin ID_USER</code>")
        return
    target_id = int(args[1])
    await user_service.set_admin_status(target_id, False)
    await message.answer(f"Status Admin dicabut dari ID <code>{target_id}</code>.")

@router.message(Command("force_gc"))
async def cmd_force_gc(message: types.Message, lfg_service: LfgService):
    if not is_owner(message.from_user.id): return
    all_data = await lfg_service.db.get_all()
    all_sessions = all_data.get("lfg", {})
    to_delete = []
    current_time = time.time()
    for session_id, data in list(all_sessions.items()):
        ts = data.get("timestamp", 0)
        if ts and current_time - ts > 7200: to_delete.append(session_id)
    for s_id in to_delete:
        if s_id in all_data["lfg"]: del all_data["lfg"][s_id]
    await lfg_service.db.save(all_data)
    await message.answer(f"<b>PEMBERSIHAN</b>: {len(to_delete)} Sesi LFG dihapus.")
