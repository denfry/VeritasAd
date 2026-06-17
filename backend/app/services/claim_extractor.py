"""Verifiable advertising claim extraction orchestrator (VeritasAd 2.0, M2).

This is the core new module of the master's release (roadmap §7.2). It takes the
multimodal signals already produced by the analysis pipeline — ASR transcript
(+ Whisper segments), OCR text, description/metadata, detected brands, disclosure
markers, CTA phrases and commercial links — and produces structured, normalized,
classified and checkworthiness-scored claims.

Three extraction strategies (roadmap §6 / §12.1 baselines) share the same
candidate→normalize→classify→score pipeline:

* ``rule_based`` — fully offline; fragments are segmented and scored with the
  rule-based classifier (:mod:`app.services.claim_classifier`), normalizer
  (:mod:`app.services.claim_normalizer`) and checkworthiness scorer
  (:mod:`app.services.checkworthiness_scorer`).
* ``llm_zero_shot`` / ``llm_few_shot`` — route through the unified
  :class:`app.services.llm_service.LLMService` (honours ``MOCK_LLM_RESPONSES``),
  then re-score deterministically and snap labels onto the canonical enums.

The orchestrator never mutates analysis state and performs no I/O beyond the LLM
call, so it is safe to run on-demand behind the ``CLAIM_EXTRACTION_ENABLED`` flag.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from app.models.database import UserPlan
from app.schemas.claims import (
    Claim,
    ClaimExtractionRequest,
    ClaimExtractionResult,
    ExtractionMethod,
    RiskLevel,
    SourceModality,
)
from app.services import claim_classifier, claim_fewshot, claim_normalizer
from app.services.checkworthiness_scorer import score_checkworthiness

logger = logging.getLogger(__name__)

# Sentence / line splitter for free text (keeps fragments claim-sized).
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+|[•·]\s*")
_MIN_FRAGMENT_LEN = 3
_MAX_FRAGMENTS = 200  # safety bound on candidates per modality

# Checkworthiness floor below which a non-typed fragment is not surfaced.
_CHECKABLE_FLOOR = 0.26


def _split_fragments(text: Optional[str]) -> List[str]:
    """Split free text into claim-sized candidate fragments."""
    if not text:
        return []
    parts = _SENTENCE_SPLIT_RE.split(text)
    out: List[str] = []
    seen: set[str] = set()
    for part in parts:
        frag = (part or "").strip(" \t\r\n-—–•·,;:")
        if len(frag) < _MIN_FRAGMENT_LEN:
            continue
        key = frag.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(frag)
        if len(out) >= _MAX_FRAGMENTS:
            break
    return out


def _locate_timestamps(
    fragment: str, segments: Optional[List[Dict[str, Any]]]
) -> Tuple[Optional[float], Optional[float]]:
    """Best-effort timestamp lookup for a fragment within Whisper segments."""
    if not segments or not fragment:
        return None, None
    frag_low = fragment.lower()
    for seg in segments:
        seg_text = str(seg.get("text") or "").strip().lower()
        if not seg_text:
            continue
        if frag_low in seg_text or seg_text in frag_low:
            try:
                return float(seg["start"]), float(seg["end"])
            except (KeyError, TypeError, ValueError):
                return None, None
    return None, None


class ClaimExtractor:
    """Extracts verifiable advertising claims from multimodal analysis signals."""

    def __init__(self) -> None:
        # Lazy import keeps the (optional) LLM clients out of the import path for
        # the offline rule-based method and unit tests.
        self._llm_service: Any = None

    # ------------------------------------------------------------------ public

    async def extract(
        self,
        request: ClaimExtractionRequest,
        *,
        plan: UserPlan = UserPlan.FREE,
    ) -> ClaimExtractionResult:
        """Extract claims using the strategy named in ``request.method``."""
        method = request.method
        model: Optional[str] = None

        if method in (ExtractionMethod.LLM_ZERO_SHOT, ExtractionMethod.LLM_FEW_SHOT):
            try:
                claims, model = await self._extract_llm(
                    request, few_shot=method == ExtractionMethod.LLM_FEW_SHOT, plan=plan
                )
            except Exception as exc:  # noqa: BLE001 - resilient fallback
                logger.warning(
                    "llm_claim_extraction_failed_falling_back_to_rules error=%s", exc
                )
                claims = self._extract_rule_based(request)
                method = ExtractionMethod.RULE_BASED
                model = None
        else:
            claims = self._extract_rule_based(request)

        claims = self._finalize(claims)
        return ClaimExtractionResult(
            claims=claims,
            method=method,
            model=model,
            content_id=request.content_id,
            source_type=request.source_type,
            source_url=request.source_url,
            stats=self._build_stats(claims),
        )

    # ------------------------------------------------------------- rule-based

    def _candidate_fragments(
        self, request: ClaimExtractionRequest
    ) -> List[Tuple[str, SourceModality, Optional[float], Optional[float]]]:
        """Collect (fragment, modality, ts_start, ts_end) candidates from all signals."""
        candidates: List[Tuple[str, SourceModality, Optional[float], Optional[float]]] = []

        # ASR: prefer time-bounded Whisper segments, else split the transcript.
        segments = request.transcript_segments or []
        if segments:
            for seg in segments:
                text = str(seg.get("text") or "").strip()
                if len(text) < _MIN_FRAGMENT_LEN:
                    continue
                try:
                    start: Optional[float] = float(seg["start"])
                    end: Optional[float] = float(seg["end"])
                except (KeyError, TypeError, ValueError):
                    start, end = None, None
                candidates.append((text, SourceModality.ASR, start, end))
        else:
            for frag in _split_fragments(request.transcript):
                candidates.append((frag, SourceModality.ASR, None, None))

        # OCR on-screen text.
        for frag in _split_fragments(request.ocr_text):
            candidates.append((frag, SourceModality.OCR, None, None))

        # Description / metadata.
        for frag in _split_fragments(request.description):
            candidates.append((frag, SourceModality.DESCRIPTION, None, None))

        return candidates

    def _extract_rule_based(self, request: ClaimExtractionRequest) -> List[Claim]:
        """Offline rule-based extraction over all multimodal signals."""
        claims: List[Claim] = []
        seen: set[str] = set()

        for raw, modality, ts_start, ts_end in self._candidate_fragments(request):
            claim_type, risk = claim_classifier.classify(raw)
            score, features = score_checkworthiness(raw)

            is_checkable = claim_type not in claim_classifier.NON_CHECKABLE_TYPES
            # Surface a fragment as a claim when it carries a measurable claim
            # type or enough checkworthiness signal. This keeps ad-free speech
            # from flooding the output while still catching scored subjective
            # fragments (e.g. a number wrapped in opinion).
            if not is_checkable and score < _CHECKABLE_FLOOR:
                continue

            key = (raw.lower(), modality.value)
            dedup = "|".join(key)
            if dedup in seen:
                continue
            seen.add(dedup)

            normalized = claim_normalizer.normalize(raw) if is_checkable else ""
            claims.append(
                Claim(
                    id="",  # assigned in _finalize
                    raw_text=raw,
                    normalized_claim=normalized,
                    source_modality=modality,
                    timestamp_start=ts_start,
                    timestamp_end=ts_end,
                    claim_type=claim_type,
                    is_checkable=is_checkable,
                    checkworthiness_score=round(score, 4),
                    risk_level=risk,
                    brand=request.brand or self._primary_brand(request),
                    evidence_needed=self._evidence_needed(is_checkable, risk, score),
                    features=features,
                )
            )
        return claims

    # --------------------------------------------------------------------- LLM

    def _get_llm_service(self):
        if self._llm_service is None:
            from app.services.llm_service import llm_service

            self._llm_service = llm_service
        return self._llm_service

    async def _extract_llm(
        self, request: ClaimExtractionRequest, *, few_shot: bool, plan: UserPlan
    ) -> Tuple[List[Claim], Optional[str]]:
        """LLM extraction; re-scores and validates against the canonical schema."""
        signals = {
            "transcript": request.transcript,
            "ocr_text": request.ocr_text,
            "description": request.description,
            "detected_brands": request.detected_brands,
            "disclosure_markers": request.disclosure_markers,
            "cta_matches": request.cta_matches,
            "commercial_urls": request.commercial_urls,
        }
        messages = claim_fewshot.build_messages(signals, few_shot=few_shot)
        llm = self._get_llm_service()
        model = llm.get_model_for_plan(plan)
        raw_response = await llm.generate_response(plan, messages)
        parsed = self._parse_llm_json(raw_response)

        claims: List[Claim] = []
        segments = request.transcript_segments or []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            raw_text = str(item.get("raw_text") or "").strip()
            if len(raw_text) < _MIN_FRAGMENT_LEN:
                continue

            claim_type = claim_classifier.coerce_claim_type(
                item.get("claim_type"), fallback_text=raw_text
            )
            risk = claim_classifier.coerce_risk_level(
                item.get("risk_level"), claim_type, fallback_text=raw_text
            )
            modality = self._coerce_modality(item.get("source_modality"))
            is_checkable = bool(
                item.get("is_checkable", claim_type not in claim_classifier.NON_CHECKABLE_TYPES)
            )
            # Checkworthiness is computed deterministically for reproducibility,
            # not taken from the model.
            score, features = score_checkworthiness(raw_text)
            normalized = str(item.get("normalized_claim") or "").strip()
            if is_checkable and not normalized:
                normalized = claim_normalizer.normalize(raw_text)
            ts_start, ts_end = _locate_timestamps(raw_text, segments)
            brand = item.get("brand") or request.brand or self._primary_brand(request)

            claims.append(
                Claim(
                    id="",
                    raw_text=raw_text,
                    normalized_claim=normalized if is_checkable else "",
                    source_modality=modality,
                    timestamp_start=ts_start,
                    timestamp_end=ts_end,
                    claim_type=claim_type,
                    is_checkable=is_checkable,
                    checkworthiness_score=round(score, 4),
                    risk_level=risk,
                    brand=str(brand) if brand else None,
                    evidence_needed=self._evidence_needed(is_checkable, risk, score),
                    features=features,
                )
            )
        return claims, model

    @staticmethod
    def _parse_llm_json(response: str) -> List[Any]:
        """Parse a JSON array from a (possibly fenced) LLM response."""
        if not response:
            return []
        text = response.strip()
        if "```" in text:
            # Strip a ```json ... ``` fence if present.
            fence = text.split("```")
            for chunk in fence:
                chunk = chunk.strip()
                if chunk.startswith("json"):
                    chunk = chunk[4:].strip()
                if chunk.startswith("[") or chunk.startswith("{"):
                    text = chunk
                    break
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Last resort: grab the outermost [...] block.
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if not match:
                logger.warning("llm_claim_response_unparseable head=%s", text[:120])
                return []
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                return []
        if isinstance(data, dict):
            # Accept {"claims": [...]} as well as a bare array.
            data = data.get("claims", [])
        return data if isinstance(data, list) else []

    # ----------------------------------------------------------------- helpers

    @staticmethod
    def _coerce_modality(value: Optional[str]) -> SourceModality:
        if value:
            normalized = str(value).strip().lower()
            for member in SourceModality:
                if normalized == member.value:
                    return member
        return SourceModality.ASR

    @staticmethod
    def _primary_brand(request: ClaimExtractionRequest) -> Optional[str]:
        """Pick the highest-confidence detected brand as a default attribution."""
        brands = request.detected_brands or []
        best: Optional[str] = None
        best_conf = -1.0
        for b in brands:
            if not isinstance(b, dict):
                continue
            name = str(b.get("name") or "").strip()
            if not name or name.lower() == "unknown":
                continue
            try:
                conf = float(b.get("confidence", 0.0))
            except (TypeError, ValueError):
                conf = 0.0
            if conf > best_conf:
                best_conf, best = conf, name
        return best

    @staticmethod
    def _evidence_needed(is_checkable: bool, risk: RiskLevel, score: float) -> bool:
        if not is_checkable:
            return False
        return risk in (RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL) or score >= 0.5

    @staticmethod
    def _finalize(claims: List[Claim]) -> List[Claim]:
        """Assign stable ids and order claims by checkworthiness (desc)."""
        ordered = sorted(claims, key=lambda c: c.checkworthiness_score, reverse=True)
        for idx, claim in enumerate(ordered, start=1):
            claim.id = f"claim_{idx:03d}"
        return ordered

    @staticmethod
    def _build_stats(claims: List[Claim]) -> Dict[str, Any]:
        by_type: Dict[str, int] = {}
        by_risk: Dict[str, int] = {}
        for c in claims:
            by_type[c.claim_type.value] = by_type.get(c.claim_type.value, 0) + 1
            by_risk[c.risk_level.value] = by_risk.get(c.risk_level.value, 0) + 1
        checkable = sum(1 for c in claims if c.is_checkable)
        mean_cw = (
            round(sum(c.checkworthiness_score for c in claims) / len(claims), 4)
            if claims
            else 0.0
        )
        return {
            "total": len(claims),
            "checkable": checkable,
            "non_checkable": len(claims) - checkable,
            "by_type": by_type,
            "by_risk": by_risk,
            "mean_checkworthiness": mean_cw,
        }


# Module-level singleton (mirrors llm_service / other services).
claim_extractor = ClaimExtractor()
