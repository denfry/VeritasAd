from pydantic import Field, field_validator, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict, Literal, Optional, Union
import secrets
import warnings
import json
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings with validation.
    All settings can be overridden via environment variables.
    
    Security notes:
    - SECRET_KEY and DATABASE_URL are required in production
    - Default values are for development only
    """

    # ==================== PROJECT ====================
    PROJECT_NAME: str = "VeritasAD"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    
    # SECRET_KEY - required in production
    SECRET_KEY: str = Field(
        default="",
        description="Secret key for signing. Required in production (min 32 chars).",
    )

    # ==================== SERVER ====================
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False

    # ==================== DATABASE ====================
    DATABASE_URL: str = Field(
        default="",
        description="Database connection URL. Required in production.",
    )
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False

    # ==================== REDIS ====================
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50

    # ==================== CELERY ====================
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"
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

    # Отключение авторизации для тестирования (development only)
    DISABLE_AUTH: bool = False

    # JWT (for future use)
    JWT_SECRET_KEY: str = Field(
        default="",
        description="JWT secret key. Required in production (min 64 chars).",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==================== SUPABASE ====================
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_JWT_SECRET: Optional[str] = None

    # ==================== RATE LIMITING ====================
    # Updated tariffs based on financial report (2026)
    FREE_TIER_DAILY_LIMIT: int = 1              # 30/month - for testing only
    STARTER_TIER_DAILY_LIMIT: int = 10          # 300/month - freelancers
    PRO_TIER_DAILY_LIMIT: int = 50              # 1,500/month - small business
    BUSINESS_TIER_DAILY_LIMIT: int = 167        # 5,000/month - agencies
    ENTERPRISE_TIER_DAILY_LIMIT: int = 667      # 20,000/month - corporations
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10

    # ==================== PAY-AS-YOU-GO CREDIT PACKAGES ====================
    # Credit packages for one-time purchases (validity period in days)
    PAYG_MICRO_CREDITS: int = 100
    PAYG_MICRO_PRICE: float = 1500.0            # 15 ₽ per analysis
    PAYG_MICRO_VALIDITY_DAYS: int = 30

    PAYG_STANDARD_CREDITS: int = 500
    PAYG_STANDARD_PRICE: float = 5000.0         # 10 ₽ per analysis
    PAYG_STANDARD_VALIDITY_DAYS: int = 60

    PAYG_PRO_CREDITS: int = 1500
    PAYG_PRO_PRICE: float = 12000.0             # 8 ₽ per analysis
    PAYG_PRO_VALIDITY_DAYS: int = 90

    PAYG_BUSINESS_CREDITS: int = 8000
    PAYG_BUSINESS_PRICE: float = 40000.0        # 5 ₽ per analysis
    PAYG_BUSINESS_VALIDITY_DAYS: int = 180

    # ==================== FILE PROCESSING ====================
    MAX_VIDEO_DURATION: int = 600  # seconds
    MAX_FILE_SIZE: int = 2 * 1024 * 1024 * 1024  # 2GB
    ALLOWED_VIDEO_EXTENSIONS: Union[List[str], str] = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    CHUNK_SIZE: int = 1024 * 1024  # 1MB

    TEMP_FILE_MAX_AGE_HOURS: int = 24
    CLEANUP_INTERVAL_MINUTES: int = 60

    # ==================== VIDEO DOWNLOAD ====================
    DOWNLOAD_TIMEOUT: int = 300  # seconds (increased for slow connections/VPN)
    DOWNLOAD_RETRIES: int = 5  # Increased retries for reliability
    DOWNLOAD_CONCURRENT_FRAGMENTS: int = 8  # Parallel fragment downloads
    DOWNLOAD_SOCKET_TIMEOUT: int = 90  # seconds (increased for slow connections/VPN)
    DOWNLOAD_FRAGMENT_RETRIES: int = 8  # Increased fragment retries
    USE_ARIA2C: bool = False  # Use aria2c as external downloader (faster)

    # ==================== ML MODELS ====================
    USE_LLM: bool = False
    WHISPER_MODEL: Literal["tiny", "base", "small", "medium", "large"] = "tiny"
    CLIP_MODEL: str = "openai/clip-vit-base-patch32"
    TORCH_DEVICE: Literal["cpu", "cuda", "mps"] = "cpu"

    HF_HOME: str = "/app/models/cache"
    # TRANSFORMERS_CACHE is deprecated, use HF_HOME instead (kept for backward compatibility)
    # TRANSFORMERS_CACHE: str = "/app/models/cache"

    # ==================== BRAND DETECTION ====================
    # Path to JSON/YAML file with custom brands list
    BRANDS_FILE: Optional[str] = "data/brands_global.json"
    # Default brands from ENV (JSON array or comma-separated)
    DEFAULT_BRANDS: Optional[str] = None
    # Enable OCR for brand detection
    ENABLE_BRAND_OCR: bool = True
    # Enable zero-shot detection for unknown brands
    ENABLE_ZERO_SHOT: bool = True
    # Detection threshold (0.0-1.0) - lowered for better sensitivity
    BRAND_DETECTION_THRESHOLD: float = 0.08
    # Max frames to sample for brand detection (increased for long videos)
    BRAND_MAX_FRAMES: int = 100
    # Frame sample interval in seconds (adaptive based on video duration)
    BRAND_FRAME_INTERVAL: float = 0.5
    # Timeout for brand detection stage in seconds
    BRAND_DETECTION_TIMEOUT: int = 240
    # Minimum confidence for brand display (filter out low confidence detections)
    BRAND_MIN_CONFIDENCE_DISPLAY: float = 0.3
    # Enable brand aliases matching
    ENABLE_BRAND_ALIASES: bool = True
    # Cloud logo detection provider: none | azure | aws
    BRAND_DETECTION_PROVIDER: Literal["none", "azure", "aws"] = "none"
    # Cloud result cache TTL (seconds)
    BRAND_CLOUD_CACHE_TTL_SECONDS: int = 3600
    # Azure Computer Vision
    AZURE_CV_ENDPOINT: Optional[str] = None
    AZURE_CV_KEY: Optional[str] = None
    # AWS Rekognition Custom Labels
    AWS_REGION: Optional[str] = None
    AWS_REKOGNITION_PROJECT_VERSION_ARN: Optional[str] = None
    AWS_REKOGNITION_MIN_CONFIDENCE: float = 70.0

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
    TELEGRAM_API_ID_RAW: Optional[str] = None  # Raw string from env
    TELEGRAM_API_ID: Optional[int] = None  # Parsed integer
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
    OTEL_SERVICE_NAME: str = "veritasad-backend"
    OTEL_EXPORTER_OTLP_ENDPOINT: Optional[str] = None

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

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate SECRET_KEY - required in production, min 32 chars."""
        if not v:
            env = info.data.get("ENVIRONMENT", "development")
            if env == "production":
                raise ValueError("SECRET_KEY is required in production environment")
            # Development - generate warning and use random value
            warnings.warn(
                "SECRET_KEY not set, using generated value (development only). "
                "Set SECRET_KEY environment variable in production.",
                UserWarning,
            )
            return secrets.token_urlsafe(32)
        
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str, info) -> str:
        """Validate DATABASE_URL - required in production."""
        if not v:
            env = info.data.get("ENVIRONMENT", "development")
            if env == "production":
                raise ValueError("DATABASE_URL is required in production environment")
            # Development default - SQLite for testing
            warnings.warn(
                "DATABASE_URL not set, using SQLite (development only). "
                "Set DATABASE_URL environment variable in production.",
                UserWarning,
            )
            return "sqlite+aiosqlite:///./veritasad_dev.db"
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, v: str, info) -> str:
        """Validate JWT_SECRET_KEY - required in production, min 64 chars."""
        if not v:
            env = info.data.get("ENVIRONMENT", "development")
            if env == "production":
                raise ValueError("JWT_SECRET_KEY is required in production environment")
            # Development - generate warning and use random value
            warnings.warn(
                "JWT_SECRET_KEY not set, using generated value (development only).",
                UserWarning,
            )
            return secrets.token_urlsafe(64)

        if len(v) < 64:
            raise ValueError("JWT_SECRET_KEY must be at least 64 characters long")
        return v

    @field_validator("TELEGRAM_API_ID_RAW")
    @classmethod
    def validate_telegram_api_id_raw(cls, v: Optional[str]) -> Optional[str]:
        """Handle empty TELEGRAM_API_ID_RAW."""
        if v is None or str(v).strip() == "":
            return None
        return v

    @field_validator("TELEGRAM_API_ID", mode="before")
    @classmethod
    def validate_telegram_api_id(cls, v):
        """Handle empty or invalid TELEGRAM_API_ID."""
        if v is None or str(v).strip() == "":
            return None
        if isinstance(v, int):
            return v
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

    @field_validator("ALLOWED_VIDEO_EXTENSIONS", mode="before")
    @classmethod
    def parse_video_extensions(cls, v):
        """Parse ALLOWED_VIDEO_EXTENSIONS from JSON string or comma-separated list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Fallback: split by comma and strip whitespace
                return [ext.strip() for ext in v.split(",") if ext.strip()]
        return v

    @model_validator(mode="after")
    def post_validate_telegram(self):
        """Post-validation to handle TELEGRAM_API_ID parsing."""
        raw = getattr(self, 'TELEGRAM_API_ID_RAW', None)
        if raw:
            raw = str(raw).strip()
            if raw and raw.isdigit():
                try:
                    self.TELEGRAM_API_ID = int(raw)
                except (ValueError, TypeError):
                    self.TELEGRAM_API_ID = None
            else:
                self.TELEGRAM_API_ID = None
        else:
            self.TELEGRAM_API_ID = None
        return self

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

    def get_default_brands(self) -> List[str]:
        """
        Get default brands list from ENV or file.
        Loads from brands_global.json with 500+ global brands.

        Returns:
            List of brand names
        """
        brands = []

        # Try to load from file first (prioritize global brands database)
        if self.BRANDS_FILE:
            brands_path = Path(self.BRANDS_FILE)
            if not brands_path.is_absolute():
                # Try to find relative to project root
                project_root = Path(__file__).parent.parent.parent.parent
                brands_path = project_root / self.BRANDS_FILE
            
            if brands_path.exists():
                try:
                    import json
                    with open(brands_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                        # Handle different JSON structures
                        if isinstance(data, list):
                            brands.extend(data)
                        elif isinstance(data, dict):
                            # Check for "brands" key (simple list)
                            if "brands" in data and isinstance(data["brands"], list):
                                brands.extend(data["brands"])
                            # Check for categorized brands (brands by category)
                            elif "brands" in data and isinstance(data["brands"], dict):
                                for category_brands in data["brands"].values():
                                    if isinstance(category_brands, list):
                                        brands.extend(category_brands)
                            # Check for "categories" key
                            if "categories" in data and isinstance(data["categories"], dict):
                                for category_brands in data["categories"].values():
                                    if isinstance(category_brands, list):
                                        brands.extend(category_brands)
                except Exception as e:
                    import warnings
                    warnings.warn(f"Failed to load brands from {self.BRANDS_FILE}: {e}")

        # Try to load from ENV (additional custom brands)
        if self.DEFAULT_BRANDS:
            try:
                import json
                # Try JSON first
                parsed = json.loads(self.DEFAULT_BRANDS)
                if isinstance(parsed, list):
                    brands.extend(parsed)
                else:
                    # Fallback: comma-separated
                    brands.extend([b.strip() for b in self.DEFAULT_BRANDS.split(",") if b.strip()])
            except json.JSONDecodeError:
                # Not JSON, treat as comma-separated
                brands.extend([b.strip() for b in self.DEFAULT_BRANDS.split(",") if b.strip()])

        # Remove duplicates while preserving order
        return list(dict.fromkeys(brands))
    
    def get_brand_aliases(self) -> Dict[str, List[str]]:
        """
        Get brand aliases mapping from brands file.
        
        Returns:
            Dictionary mapping brand names to their aliases
        """
        if self.BRANDS_FILE:
            brands_path = Path(self.BRANDS_FILE)
            if not brands_path.is_absolute():
                project_root = Path(__file__).parent.parent.parent.parent
                brands_path = project_root / self.BRANDS_FILE
            
            if brands_path.exists():
                try:
                    import json
                    with open(brands_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict) and "aliases" in data:
                            return data["aliases"]
                except Exception as e:
                    import warnings
                    warnings.warn(f"Failed to load brand aliases: {e}")
        
        return {}


settings = Settings()

# Create directories on startup
settings.create_directories()
