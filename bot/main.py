import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import settings
from handlers import router

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "development" else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main():
    """Main bot entry point."""
    
    # Check if bot is configured
    if not settings.is_configured():
        logger.error("Bot is not configured. Set TELEGRAM_BOT_TOKEN in .env file")
        # Keep running but don't start polling (for Docker health checks)
        while True:
            await asyncio.sleep(60)
    
    # Initialize Redis
    redis_client = None
    try:
        redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        await redis_client.ping()
        logger.info(f"Connected to Redis: {settings.REDIS_URL}")
        storage = RedisStorage(redis_client)
    except Exception as e:
        logger.warning(f"Redis connection failed, using memory storage: {e}")
        from aiogram.fsm.storage.memory import MemoryStorage
        storage = MemoryStorage()

    # Initialize Bot and Dispatcher
    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    # Include routers
    dp.include_router(router)

    # Set bot commands
    await set_bot_commands(bot)

    # Start polling
    logger.info("Bot started - polling for messages")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Cleanup
        await dp.storage.close()
        await bot.session.close()
        if redis_client:
            await redis_client.aclose()


async def set_bot_commands(bot: Bot):
    """Set bot menu commands."""
    from aiogram.types import BotCommand
    
    commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="analyze", description="Analyze a video"),
        BotCommand(command="profile", description="View your profile"),
        BotCommand(command="history", description="View analysis history"),
        BotCommand(command="help", description="Show help message"),
    ]
    
    try:
        await bot.set_my_commands(commands)
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.warning(f"Failed to set bot commands: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {e}", exc_info=True)
        sys.exit(1)
