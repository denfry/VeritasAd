"""Cloud logo detection service (Azure Computer Vision / AWS Rekognition)."""
from __future__ import annotations

import hashlib
import io
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from PIL import Image
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class _CacheItem:
    expires_at: float
    payload: List[Dict[str, float | str]]


class CloudBrandDetector:
    """Optional cloud provider integration for logo/brand recognition."""

    def __init__(self) -> None:
        self.provider = (settings.BRAND_DETECTION_PROVIDER or "none").lower().strip()
        self.cache_ttl = max(30, int(settings.BRAND_CLOUD_CACHE_TTL_SECONDS))
        self._cache: Dict[str, _CacheItem] = {}

        self.azure_endpoint = (settings.AZURE_CV_ENDPOINT or "").rstrip("/")
        self.azure_key = settings.AZURE_CV_KEY or ""
        self.aws_region = settings.AWS_REGION or ""
        self.aws_custom_model_arn = settings.AWS_REKOGNITION_PROJECT_VERSION_ARN or ""
        self.aws_min_confidence = float(settings.AWS_REKOGNITION_MIN_CONFIDENCE)

    def is_enabled(self) -> bool:
        if self.provider == "azure":
            return bool(self.azure_endpoint and self.azure_key)
        if self.provider == "aws":
            return bool(self.aws_region and self.aws_custom_model_arn)
        return False

    def detect_brands(
        self,
        frames: Sequence[Image.Image],
        timestamps: Sequence[float],
        *,
        max_frames: int = 20,
    ) -> Dict[str, object]:
        """Detect brands for selected frames via configured cloud provider."""
        if not self.is_enabled():
            return {"detected_brands": [], "provider": "none"}

        detections: List[Dict[str, object]] = []
        frame_limit = min(len(frames), len(timestamps), max_frames)

        for idx in range(frame_limit):
            image = frames[idx]
            timestamp = timestamps[idx]
            try:
                if self.provider == "azure":
                    frame_dets = self._detect_frame_azure(image)
                elif self.provider == "aws":
                    frame_dets = self._detect_frame_aws(image)
                else:
                    frame_dets = []
            except Exception as exc:
                logger.warning("cloud_brand_detection_frame_failed", provider=self.provider, error=str(exc))
                frame_dets = []

            for det in frame_dets:
                detections.append(
                    {
                        "name": str(det.get("name", "")).strip(),
                        "confidence": float(det.get("confidence", 0.0)),
                        "timestamp": float(timestamp),
                        "source": f"cloud_{self.provider}",
                    }
                )

        return {"detected_brands": detections, "provider": self.provider}

    def _detect_frame_azure(self, image: Image.Image) -> List[Dict[str, object]]:
        image_bytes = self._to_jpeg_bytes(image)
        cache_key = f"azure:{self._hash_bytes(image_bytes)}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        url = f"{self.azure_endpoint}/vision/v3.2/analyze"
        params = {"visualFeatures": "Brands", "language": "en"}
        headers = {
            "Ocp-Apim-Subscription-Key": self.azure_key,
            "Content-Type": "application/octet-stream",
        }
        response = requests.post(url, headers=headers, params=params, data=image_bytes, timeout=8)
        response.raise_for_status()
        payload = response.json() or {}

        detections: List[Dict[str, object]] = []
        for item in payload.get("brands", []):
            name = str(item.get("name", "")).strip()
            confidence = float(item.get("confidence", 0.0))
            if name:
                detections.append({"name": name, "confidence": confidence})

        self._set_cached(cache_key, detections)
        return detections

    def _detect_frame_aws(self, image: Image.Image) -> List[Dict[str, object]]:
        image_bytes = self._to_jpeg_bytes(image)
        cache_key = f"aws:{self._hash_bytes(image_bytes)}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            import boto3  # type: ignore
        except Exception as exc:
            logger.warning("boto3_not_available_for_aws_detection", error=str(exc))
            return []

        client = boto3.client("rekognition", region_name=self.aws_region)
        response = client.detect_custom_labels(
            ProjectVersionArn=self.aws_custom_model_arn,
            Image={"Bytes": image_bytes},
            MinConfidence=self.aws_min_confidence,
        )

        detections: List[Dict[str, object]] = []
        for item in response.get("CustomLabels", []):
            name = str(item.get("Name", "")).strip()
            confidence = float(item.get("Confidence", 0.0)) / 100.0
            if name:
                detections.append({"name": name, "confidence": confidence})

        self._set_cached(cache_key, detections)
        return detections

    def _to_jpeg_bytes(self, image: Image.Image) -> bytes:
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85, optimize=True)
        return buffer.getvalue()

    def _hash_bytes(self, payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()

    def _get_cached(self, key: str) -> Optional[List[Dict[str, float | str]]]:
        item = self._cache.get(key)
        now = time.time()
        if item and item.expires_at > now:
            return item.payload
        if item:
            self._cache.pop(key, None)
        return None

    def _set_cached(self, key: str, payload: List[Dict[str, float | str]]) -> None:
        self._cache[key] = _CacheItem(expires_at=time.time() + self.cache_ttl, payload=payload)
