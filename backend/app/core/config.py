from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Literal, Optional
import secrets
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings with validation.
    All settings can be overridden via environment variables.
    """

    # ==================== PROJECT ====================
    PROJECT_NAME: str = "VeritasAD"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "production"
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))

    # ==================== SERVER ====================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False

    # ==================== DATABASE ====================
    DATABASE_URL: str = "postgresql+asyncpg://veritasad:veritasad123@localhost:5432/veritasad"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False

    # Database URL validation removed - SQLite is allowed in development

    # ==================== REDIS ====================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # ==================== CELERY ====================
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 600
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1
    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 50

    # ==================== SECURITY ====================
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://veritasad.ai"]
    CORS_ALLOW_CREDENTIALS: bool = True
    TRUSTED_HOSTS: List[str] = ["localhost", "veritasad.ai", "*.veritasad.ai"]

    API_KEY_LENGTH: int = 32
    API_KEY_HEADER: str = "X-API-Key"

    # JWT (for future use)
    JWT_SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(64))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==================== RATE LIMITING ====================
    FREE_TIER_DAILY_LIMIT: int = 100
    PRO_TIER_DAILY_LIMIT: int = 10000
    ENTERPRISE_TIER_DAILY_LIMIT: int = 999999
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # ==================== FILE PROCESSING ====================
    MAX_VIDEO_DURATION: int = 600  # seconds
    MAX_FILE_SIZE: int = 2 * 1024 * 1024 * 1024  # 2GB
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    CHUNK_SIZE: int = 1024 * 1024  # 1MB

    TEMP_FILE_MAX_AGE_HOURS: int = 24
    CLEANUP_INTERVAL_MINUTES: int = 60

    # ==================== ML MODELS ====================
    USE_LLM: bool = False
    WHISPER_MODEL: Literal["tiny", "base", "small", "medium", "large"] = "tiny"
    CLIP_MODEL: str = "openai/clip-vit-base-patch32"
    TORCH_DEVICE: Literal["cpu", "cuda", "mps"] = "cpu"

    HF_HOME: str = "/app/models/cache"
    TRANSFORMERS_CACHE: str = "/app/models/cache"

    # ==================== PATHS ====================
    DATA_DIR: str = "/app/data"
    MODELS_DIR: str = "/app/models"
    REPORTS_DIR: str = "/app/data/reports"
    TEMP_DIR: str = "/app/data/temp"
    UPLOAD_DIR: str = "/app/data/uploads"

    @computed_field
    @property
    def data_path(self) -> Path:
        return Path(self.DATA_DIR)

    @computed_field
    @property
    def reports_path(self) -> Path:
        return Path(self.REPORTS_DIR)

    @computed_field
    @property
    def temp_path(self) -> Path:
        return Path(self.TEMP_DIR)

    @computed_field
    @property
    def upload_path(self) -> Path:
        return Path(self.UPLOAD_DIR)

    # ==================== TELEGRAM BOT ====================
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_API_ID: Optional[int] = None
    TELEGRAM_API_HASH: Optional[str] = None
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_WEBHOOK_PATH: str = "/webhook/telegram"

    # ==================== PAYMENT ====================
    YOOKASSA_SHOP_ID: Optional[str] = None
    YOOKASSA_SECRET_KEY: Optional[str] = None
    YOOKASSA_RETURN_URL: str = "https://veritasad.ai/payment/success"

    # ==================== MONITORING ====================
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = False

    # ==================== EMAIL ====================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "VeritasAD <noreply@veritasad.ai>"

    # ==================== EXTERNAL SERVICES ====================
    OPENAI_API_KEY: Optional[str] = None
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    def create_directories(self) -> None:
        """Create required directories if they don't exist"""
        for path in [
            self.data_path,
            self.reports_path,
            self.temp_path,
            self.upload_path,
            Path(self.MODELS_DIR),
        ]:
            path.mkdir(parents=True, exist_ok=True)


settings = Settings()

# Create directories on startup
settings.create_directories()