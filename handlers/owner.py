from aiogram import Router, types
from aiogram.filters import Command
from config import settings
from services.user_service import UserService
from services.lfg_service import LfgService
from utils.group_logger import send_log
import psutil
import time

router = Router()

def is_owner(user_id: int) -> bool:
    return user_id == settings.owner_id

@router.message(Command("sys"))
async def cmd_sys(message: types.Message, user_service: UserService, lfg_service: LfgService):
    if not is_owner(message.from_user.id):
        return
        
    start_time = time.time()
    
    # Gathering data
    user_count = await user_service.get_user_count()
    all_data = await lfg_service.db.get_all()
    all_lfg = all_data.get("lfg", {})
    active_lfg_count = len([k for k,v in all_lfg.items() if v.get("status") == "open"])
    
    # System resources
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    uptime = int(time.time() - psutil.boot_time())
    
    text = (
        f"<b>SISTEM KONTROL PUSAT</b>\n"
        f"----------------------------------------\n"
        f"<b>RAM Usage:</b> {ram_usage}%\n"
        f"<b>Waktu Aktif:</b> {uptime} dtk\n"
        f"<b>Total Pengguna:</b> {user_count}\n"
        f"<b>Total Sesi LFG:</b> {active_lfg_count}\n"
        f"----------------------------------------\n"
        f"<code>/addadmin [user_id]</code> - Berikan hak Admin\n"
        f"<code>/deladmin [user_id]</code> - Cabut hak Admin"
    )
    
    # Check if get_close_kb exists in general, else use a simple builder
    try:
        from handlers.general import get_close_kb
        kb = get_close_kb()
    except ImportError:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.button(text="❌ Tutup", callback_data="close_msg")
        kb = builder.as_markup()

    await message.answer(text, reply_markup=kb)

@router.message(Command("addadmin"))
async def cmd_addadmin(message: types.Message, user_service: UserService):
    if not is_owner(message.from_user.id): return
    
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("Format: <code>/addadmin ID_USER</code>")
        return
        
    target_id = int(args[1])
    await user_service.set_admin_status(target_id, True)
    await send_log(message.bot, "ADMIN_ACTION", f"Owner mengangkat ID <code>{target_id}</code> menjadi Admin.")
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
    await send_log(message.bot, "ADMIN_ACTION", f"Owner mencabut akses Admin dari ID <code>{target_id}</code>.")
    await message.answer(f"Status Admin dicabut dari ID <code>{target_id}</code>.")

@router.message(Command("force_gc"))
async def cmd_force_gc(message: types.Message, lfg_service: LfgService):
    if not is_owner(message.from_user.id): return
    
    all_data = await lfg_service.db.get_all()
    all_sessions = all_data.get("lfg", {})
    to_delete = []
    current_time = time.time()
    
    # This manual cleanup is less efficient with JSON but safe for small scale
    for session_id, data in list(all_sessions.items()):
        # Note: session DTO might not have timestamp if not saved, 
        # but the raw data in lfg should have it from previous versions 
        # or we add it to create_session.
        ts = data.get("timestamp", 0)
        if ts and current_time - ts > 7200: # 2 hours
            to_delete.append(session_id)
            
    for s_id in to_delete:
        if s_id in all_data["lfg"]:
            del all_data["lfg"][s_id]
        
    await lfg_service.db.save(all_data)
    await message.answer(f"<b>PEMBERSIHAN SISTEM</b>\n{len(to_delete)} Sesi LFG kadaluarsa dihapus secara manual.")
