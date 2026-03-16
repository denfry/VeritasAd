import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp import AiohttpRequestHandler
from aiogram.webhook.security import BaseHashFilter
from aiogram.types import ErrorEvent
from aiohttp import web
from redis.asyncio import Redis

from config import settings
from handlers import router

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "development" else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class SecretHashFilter(BaseHashFilter):
    """Filter to verify webhook secret."""

    def __init__(self, secret: str):
        super().__init__(secret)
        self.secret = secret

    async def __call__(self, event: ErrorEvent) -> bool:
        return True  # Allow all errors for now


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

    # Check if we should use webhook or polling
    if settings.WEBHOOK_URL:
        # Production mode: use webhook
        await setup_webhook(bot, dp)
    else:
        # Development mode: use polling
        await start_polling(bot, dp, redis_client)


async def setup_webhook(bot: Bot, dp: Dispatcher):
    """Setup webhook for production."""
    webhook_url = f"{settings.WEBHOOK_URL.rstrip('/')}{settings.WEBHOOK_PATH}"

    logger.info(f"Setting up webhook at: {webhook_url}")

    try:
        # Set webhook
        await bot.set_webhook(
            webhook_url,
            secret_token=settings.WEBHOOK_SECRET,
            drop_pending_updates=True,
        )
        logger.info(f"Webhook set successfully: {webhook_url}")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        logger.info("Falling back to polling mode")
        await start_polling(bot, dp, None)
        return

    # Create aiohttp application
    app = web.Application()

    # Create request handler
    request_handler = AiohttpRequestHandler(
        dispatcher=dp,
        secret_token=settings.WEBHOOK_SECRET,
    )

    # Register webhook handler
    app.router.add_post(settings.WEBHOOK_PATH, request_handler.handle)

    # Health check endpoint
    app.router.add_get("/health", lambda _: web.Response(text="OK"))

    # Run aiohttp server
    runner = web.AppRunner(app)
    await runner.setup()

    # Start webhook server (internal)
    port = 8443
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logger.info(f"Webhook server started on port {port}")

    # Keep running
    try:
        await asyncio.Event().wait()
    finally:
        await bot.session.close()


async def start_polling(bot: Bot, dp: Dispatcher, redis_client):
    """Start polling mode for development."""
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
