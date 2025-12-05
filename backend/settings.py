import os
from functools import lru_cache


class Settings:
    """Centralized runtime configuration."""

    database_url: str
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str
    storage_dir: str
    api_key: str
    use_minio: bool
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str

    def __init__(self) -> None:
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://veritasad:veritasad@localhost:5432/veritasad",
        )
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.celery_broker_url = os.getenv("CELERY_BROKER_URL", self.redis_url)
        self.celery_result_backend = os.getenv("CELERY_RESULT_BACKEND", self.redis_url)
        # Local storage folder for media/outputs in stage 1 (can swap to S3/MinIO later)
        self.storage_dir = os.getenv("STORAGE_DIR", "../data/raw")
        # Simple API key for MVP auth
        self.api_key = os.getenv("API_KEY", "dev-key")
        # Object storage (MinIO/S3 compatible)
        self.use_minio = os.getenv("USE_MINIO", "false").lower() == "true"
        self.minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
        self.minio_bucket = os.getenv("MINIO_BUCKET", "veritasad")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

