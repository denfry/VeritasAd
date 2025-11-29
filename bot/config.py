from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    API_URL: str = "http://backend:8000"
    REDIS_URL: str = "redis://redis:6379/2"
    
    # Webhook
    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_PATH: str = "/webhook/telegram"
    WEBHOOK_SECRET: Optional[str] = None
    
    # Bot settings
    BOT_ADMIN_IDS: list[int] = []
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
