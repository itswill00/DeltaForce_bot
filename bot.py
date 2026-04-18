import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import settings

# Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Initialize bot and dispatcher
bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Middlewares
from middlewares.error_handler import ErrorHandlerMiddleware
from middlewares.db_session import DbSessionMiddleware
from middlewares.registration import RegistrationMiddleware
from middlewares.event_logger import EventLoggerMiddleware
from middlewares.throttling import ThrottlingMiddleware

async def notify_restart_success():
    """Checks for restart arguments and notifies the owner."""
    if "--restart" in sys.argv:
        try:
            idx = sys.argv.index("--restart")
            chat_id = int(sys.argv[idx + 1])
            msg_id = int(sys.argv[idx + 2])
            
            from utils.style_utils import get_header
            text = get_header("Sistem Online", "✅")
            text += "Unit telah berhasil diperbarui dan kembali operasional."
            
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text=text
            )
            logging.info(f"Restart notification sent to chat {chat_id}")
        except Exception as e:
            logging.error(f"Failed to send restart notification: {e}")

async def main():
    # 1. Setup Enterprise Middlewares (Outermost First)
    dp.update.outer_middleware(ErrorHandlerMiddleware())            # Global Error Sentinel
    dp.update.outer_middleware(ThrottlingMiddleware(rate_limit=1.5)) # Anti-Spam
    dp.update.outer_middleware(DbSessionMiddleware())               # DB Session
    dp.update.outer_middleware(EventLoggerMiddleware())             # Interaction Logger
    
    dp.message.middleware(RegistrationMiddleware())                  # Gatekeeper
    dp.callback_query.middleware(RegistrationMiddleware())           # Gatekeeper
    
    # 2. Include Routers
    from handlers import general, profile, lfg, meta, leaderboard, admin, owner, operator, shop, inline, group_settings, intel, trivia
    
    dp.include_router(general.router)
    dp.include_router(profile.router)
    dp.include_router(lfg.router)
    dp.include_router(meta.router)
    dp.include_router(leaderboard.router)
    dp.include_router(intel.router)
    dp.include_router(shop.router)
    dp.include_router(operator.router)
    dp.include_router(trivia.router)
    dp.include_router(inline.router)
    dp.include_router(group_settings.router)
    dp.include_router(admin.router)
    dp.include_router(owner.router)

    logging.info(f"Delta Force Bot starting with JSON Persistence ({settings.local_db_path})...")
    
    from utils.scheduler import lfg_garbage_collector, auto_intel_scheduler, database_backup_scheduler
    from utils.news_updater import auto_news_fetcher
    
    # Background tasks
    asyncio.create_task(lfg_garbage_collector())
    asyncio.create_task(auto_intel_scheduler(bot))
    asyncio.create_task(auto_news_fetcher(bot))
    asyncio.create_task(database_backup_scheduler(bot))
    
    # Notify restart success
    asyncio.create_task(notify_restart_success())

    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        if settings.bot_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            logging.error("CRITICAL: Bot token not configured.")
        else:
            asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped.")
    except Exception as e:
        logging.critical(f"Bot crashed: {e}", exc_info=True)
