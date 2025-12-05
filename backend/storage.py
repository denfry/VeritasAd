from pathlib import Path
from typing import Optional

from minio import Minio
from minio.error import S3Error

from .settings import get_settings

settings = get_settings()

_client: Optional[Minio] = None


def _get_client() -> Minio:
    global _client
    if _client:
        return _client
    _client = Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )
    # Ensure bucket
    if not _client.bucket_exists(settings.minio_bucket):
        _client.make_bucket(settings.minio_bucket)
    return _client


def upload_file(path: Path, object_name: str) -> str:
    """Upload file to MinIO and return presigned URL."""
    client = _get_client()
    try:
        client.fput_object(settings.minio_bucket, object_name, str(path))
        url = client.get_presigned_url("GET", settings.minio_bucket, object_name)
        return url
    except S3Error as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"MinIO upload failed: {exc}")

