from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.ml.ad_dataset import validate_record
from app.ml.ad_model import HybridAdClassifier

logger = logging.getLogger(__name__)


class AdModelScorer:
    """Optional model scorer with deterministic fallback behavior."""

    def __init__(self, *, artifact_path: str | Path | None, enabled: bool) -> None:
        self.artifact_path = Path(artifact_path) if artifact_path else None
        self.enabled = enabled
        self._model: HybridAdClassifier | None = None
        self._load_failed = False

    def _load_model(self) -> HybridAdClassifier | None:
        if not self.enabled or not self.artifact_path:
            return None
        if self._model is not None:
            return self._model
        if self._load_failed or not self.artifact_path.exists():
            return None

        try:
            self._model = HybridAdClassifier.load(self.artifact_path)
        except Exception as exc:
            self._load_failed = True
            logger.warning("ad_model_load_failed", extra={"path": str(self.artifact_path), "error": str(exc)})
            return None
        return self._model

    def score(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        model = self._load_model()
        if model is None:
            return None

        inference_payload = dict(payload)
        inference_payload.setdefault("record_id", "inference::current")
        inference_payload.setdefault("source_key", inference_payload["record_id"])
        inference_payload.setdefault("content_type", "inference")
        inference_payload.setdefault("status", "completed")
        inference_payload.setdefault("review_label", inference_payload.get("ad_classification") or "no_ad")

        try:
            record = validate_record(inference_payload)
            prediction = model.predict(record)
        except Exception as exc:
            logger.warning("ad_model_score_failed", extra={"error": str(exc)})
            return None

        return {
            "model_version": prediction.model_version,
            "model_confidence": prediction.confidence,
            "model_class_probabilities": prediction.class_probabilities,
            "ad_classification": prediction.predicted_class,
            "has_advertising": prediction.has_advertising,
        }
