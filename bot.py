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
from middlewares.db_session import DbSessionMiddleware
from middlewares.registration import RegistrationMiddleware

async def main():
    # 1. Setup Middlewares
    # We keep the same middleware names to avoid breaking the router structure
    dp.update.outer_middleware(DbSessionMiddleware())
    dp.message.middleware(RegistrationMiddleware())
    dp.callback_query.middleware(RegistrationMiddleware())
    
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
    
    from utils.scheduler import lfg_garbage_collector, auto_intel_scheduler
    from utils.news_updater import auto_news_fetcher
    
    # Background tasks
    asyncio.create_task(lfg_garbage_collector())
    asyncio.create_task(auto_intel_scheduler(bot))
    asyncio.create_task(auto_news_fetcher(bot))

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
