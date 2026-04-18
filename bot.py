import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Import routers from handlers
from handlers.general import router as general_router
from handlers.profile import router as profile_router
from handlers.lfg import router as lfg_router
from handlers.meta import router as meta_router
from handlers.leaderboard import router as leaderboard_router
from handlers.admin import router as admin_router
from handlers.owner import router as owner_router
from handlers.operator import router as operator_router
from handlers.shop import router as shop_router
from handlers.inline import router as inline_router
from handlers.group_settings import router as group_settings_router
from handlers.intel import router as intel_router
from handlers.trivia import router as trivia_router

from middlewares.registration import RegistrationMiddleware

async def main():
    # Setup global middlewares
    dp.message.middleware(RegistrationMiddleware())
    dp.callback_query.middleware(RegistrationMiddleware())
    
    # Include routers in proper order
    dp.include_router(general_router)
    dp.include_router(profile_router)
    dp.include_router(lfg_router)
    dp.include_router(meta_router)
    dp.include_router(leaderboard_router)
    dp.include_router(intel_router)
    dp.include_router(shop_router)
    dp.include_router(operator_router)
    dp.include_router(trivia_router)
    dp.include_router(inline_router)
    dp.include_router(group_settings_router)
    dp.include_router(admin_router)
    dp.include_router(owner_router)

    logging.info("Starting Delta Force Bot...")
    
    from utils.scheduler import lfg_garbage_collector, auto_intel_scheduler
    from utils.news_updater import auto_news_fetcher
    
    asyncio.create_task(lfg_garbage_collector())
    asyncio.create_task(auto_intel_scheduler(bot))
    asyncio.create_task(auto_news_fetcher(bot))

    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        if settings.bot_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            print("ERROR: Please set your bot_token in the .env file or config.yaml")
        else:
            asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped!")
