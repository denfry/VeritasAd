"""Pydantic schemas for verifiable advertising claim extraction (VeritasAd 2.0, M2).

These models are the data contract for the claim-extraction subsystem described in
the master's roadmap (``docs/research/roadmaps/master-2.0.md`` §7–§10) and the dataset
schema (``docs/research/datasets/claims/schema.md``):

* :class:`Claim` mirrors the roadmap §7.3 result object (raw → normalized → typed →
  risk-scored → checkworthiness-scored).
* :class:`ClaimExtractionRequest` is the on-demand API input: the multimodal signals
  already produced by the analysis pipeline (ASR transcript, OCR text, metadata,
  brand/disclosure/link evidence).
* :class:`ClaimExtractionResult` is the API output plus aggregate statistics.

The export layer (``app.services.claim_export``) maps :class:`Claim` onto the JSONL
row format of the dataset schema. Field naming follows roadmap §7.3 here; the dataset
field names (``fragment``/``modality``/``raw_claim``) are produced at export time.
"""
from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, computed_field, field_validator


class ClaimType(str, enum.Enum):
    """Advertising claim taxonomy (roadmap §8)."""

    QUANTITATIVE = "quantitative"
    COMPARATIVE = "comparative"
    SUPERLATIVE = "superlative"
    TEMPORAL = "temporal"
    FINANCIAL = "financial"
    HEALTH_SAFETY = "health_safety"
    LEGAL_CERTIFICATION = "legal_certification"
    PARTNERSHIP = "partnership"
    AVAILABILITY = "availability"
    SUBJECTIVE = "subjective"
    NON_CHECKABLE = "non_checkable"


class RiskLevel(str, enum.Enum):
    """Claim risk levels (roadmap §9)."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SourceModality(str, enum.Enum):
    """Modality a claim fragment was extracted from (dataset schema ``modality``)."""

    OCR = "ocr"
    ASR = "asr"
    METADATA = "metadata"
    LINK = "link"
    DESCRIPTION = "description"


class ExtractionMethod(str, enum.Enum):
    """Claim-extraction strategy.

    ``rule_based`` is fully offline (no API keys); the LLM variants route through
    the unified :class:`app.services.llm_service.LLMService` and honour
    ``MOCK_LLM_RESPONSES`` for development.
    """

    RULE_BASED = "rule_based"
    LLM_ZERO_SHOT = "llm_zero_shot"
    LLM_FEW_SHOT = "llm_few_shot"


# Checkworthiness scale buckets (roadmap §10 / dataset schema "Checkworthiness scoring").
def checkworthiness_bucket(score: float) -> str:
    """Map a continuous checkworthiness score in [0, 1] to its priority bucket."""
    if score <= 0.25:
        return "almost_none"
    if score <= 0.50:
        return "low"
    if score <= 0.75:
        return "desirable"
    return "required"


class Claim(BaseModel):
    """A single extracted, normalized, classified and scored advertising claim."""

    id: str = Field(..., description="Stable per-result claim id, e.g. 'claim_001'.")
    raw_text: str = Field(..., description="Original fragment as it appears in the content.")
    normalized_claim: str = Field(
        "", description="Claim rewritten into a strict, verifiable form."
    )
    source_modality: SourceModality = Field(
        SourceModality.ASR, description="Modality the fragment was extracted from."
    )
    timestamp_start: Optional[float] = Field(
        None, ge=0, description="Fragment start time in the source media (seconds)."
    )
    timestamp_end: Optional[float] = Field(
        None, ge=0, description="Fragment end time in the source media (seconds)."
    )
    claim_type: ClaimType = Field(
        ClaimType.SUBJECTIVE, description="Claim class from the taxonomy."
    )
    is_checkable: bool = Field(
        False, description="Whether the claim is in principle externally verifiable."
    )
    checkworthiness_score: float = Field(
        0.0, ge=0.0, le=1.0, description="Priority of external verification, in [0, 1]."
    )
    risk_level: RiskLevel = Field(RiskLevel.LOW, description="Risk level of the claim.")
    brand: Optional[str] = Field(None, description="Brand / advertiser the claim refers to.")
    evidence_needed: bool = Field(
        False, description="Whether external evidence is needed to verify the claim."
    )
    features: Dict[str, float] = Field(
        default_factory=dict,
        description="Checkworthiness feature contributions (explainability).",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def checkworthiness_bucket(self) -> str:
        """Human-readable checkworthiness bucket label (roadmap §10)."""
        return checkworthiness_bucket(self.checkworthiness_score)

    @field_validator("checkworthiness_score")
    @classmethod
    def _clamp_score(cls, v: float) -> float:
        return max(0.0, min(1.0, float(v)))


class ClaimExtractionRequest(BaseModel):
    """On-demand claim-extraction input.

    All signal fields are optional so the endpoint can be driven either by raw text
    or by the multimodal output already stored on an analysis record.
    """

    transcript: Optional[str] = Field(None, description="ASR transcript text.")
    transcript_segments: Optional[List[Dict[str, Any]]] = Field(
        None, description="Whisper segments: list of {start, end, text}."
    )
    ocr_text: Optional[str] = Field(None, description="On-screen OCR text.")
    description: Optional[str] = Field(None, description="Source description / metadata text.")
    detected_brands: Optional[List[Dict[str, Any]]] = Field(
        None, description="Detected brands: list of {name, confidence, source, ...}."
    )
    disclosure_markers: Optional[List[str]] = Field(None, description="Disclosure markers.")
    cta_matches: Optional[List[str]] = Field(None, description="Matched CTA phrases.")
    commercial_urls: Optional[List[str]] = Field(None, description="Commercial / tracking URLs.")
    method: ExtractionMethod = Field(
        ExtractionMethod.RULE_BASED, description="Extraction strategy to use."
    )

    # Provenance, echoed into the result and the export rows.
    content_id: Optional[str] = Field(None, description="Stable id of the source content.")
    source_type: Optional[str] = Field(None, description="video | post | screenshot | url.")
    source_url: Optional[str] = Field(None, description="URL of the source material.")
    brand: Optional[str] = Field(None, description="Override brand for all claims.")


class ClaimExtractionResult(BaseModel):
    """Claim-extraction output: the claims plus method/model provenance and stats."""

    claims: List[Claim] = Field(default_factory=list)
    method: ExtractionMethod = Field(ExtractionMethod.RULE_BASED)
    model: Optional[str] = Field(None, description="LLM model used (None for rule-based).")
    content_id: Optional[str] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None
    stats: Dict[str, Any] = Field(
        default_factory=dict,
        description="Aggregates: counts by type/risk, checkable count, mean checkworthiness.",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_claims(self) -> int:
        return len(self.claims)
