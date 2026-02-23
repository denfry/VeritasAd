from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Telegram bot settings with validation."""
    
    TELEGRAM_BOT_TOKEN: str = ""
    API_URL: str = "http://backend:8000"
    REDIS_URL: str = "redis://localhost:6379/2"

    # Webhook (optional - for production)
    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_PATH: str = "/webhook/telegram"
    WEBHOOK_SECRET: Optional[str] = None

    # Bot admin IDs (for debugging)
    BOT_ADMIN_IDS: str = ""

    # Environment
    ENVIRONMENT: str = "development"

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }

    def is_configured(self) -> bool:
        """Check if bot is properly configured."""
        return bool(self.TELEGRAM_BOT_TOKEN and self.TELEGRAM_BOT_TOKEN != "your_bot_token_here")


settings = Settings()
