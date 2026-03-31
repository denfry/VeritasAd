from __future__ import annotations

from typing import Any, Dict, Iterable, List


def merge_brand_detections(*brand_groups: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}

    for group in brand_groups:
        for brand in group or []:
            name = str(brand.get("name", "")).strip()
            if not name:
                continue

            key = name.casefold()
            confidence = float(brand.get("confidence", 0.0))
            timestamps = [
                float(ts)
                for ts in (brand.get("timestamps") or [])
                if isinstance(ts, (int, float))
            ]
            source = str(brand.get("source", "unknown"))
            detections = int(
                brand.get(
                    "detections",
                    brand.get("frame_count", brand.get("occurrences", max(1, len(timestamps) or 1))),
                )
            )
            total_exposure_seconds = float(brand.get("total_exposure_seconds", 0.0))

            if key not in merged:
                merged[key] = {
                    "name": name,
                    "confidence": confidence,
                    "timestamps": timestamps[:],
                    "source": source,
                    "frame_count": int(brand.get("frame_count", max(1, len(timestamps) or detections or 1))),
                    "detections": max(1, detections),
                    "occurrences": int(brand.get("occurrences", max(1, detections))),
                    "total_exposure_seconds": total_exposure_seconds,
                    "is_unknown": bool(brand.get("is_unknown", False)),
                    "is_discovered": bool(brand.get("is_discovered", False)),
                }
                continue

            current = merged[key]
            current["confidence"] = max(float(current["confidence"]), confidence)
            current["timestamps"].extend(timestamps)
            current["frame_count"] = int(current["frame_count"]) + int(
                brand.get("frame_count", max(1, len(timestamps) or 1))
            )
            current["detections"] = int(current["detections"]) + max(1, detections)
            current["occurrences"] = int(current["occurrences"]) + int(
                brand.get("occurrences", max(1, detections))
            )
            current["total_exposure_seconds"] = max(
                float(current["total_exposure_seconds"]),
                total_exposure_seconds,
            )
            if source not in str(current["source"]):
                current["source"] = f"{current['source']},{source}"
            current["is_unknown"] = bool(current["is_unknown"] or brand.get("is_unknown", False))
            current["is_discovered"] = bool(
                current["is_discovered"] or brand.get("is_discovered", False)
            )

    final_brands = []
    for item in merged.values():
        item["timestamps"] = sorted(set(float(ts) for ts in item["timestamps"]))
        final_brands.append(item)

    final_brands.sort(key=lambda x: float(x.get("confidence", 0.0)), reverse=True)
    return final_brands


def compute_brand_signal_score(detected_brands: List[Dict[str, Any]] | None) -> float:
    detected_brands = detected_brands or []
    if not detected_brands:
        return 0.0

    evidence_scores: List[float] = []
    for brand in detected_brands:
        confidence = float(brand.get("confidence", 0.0))
        detections = int(
            brand.get("detections", brand.get("occurrences", brand.get("frame_count", 1)))
        )
        exposure = float(brand.get("total_exposure_seconds", 0.0))
        source = str(brand.get("source", "")).lower()
        is_unknown = bool(brand.get("is_unknown", False))
        is_discovered = bool(brand.get("is_discovered", False))

        score = confidence
        if detections >= 2:
            score += 0.08
        if detections >= 4:
            score += 0.06
        if exposure >= 1.5:
            score += 0.07
        if exposure >= 4:
            score += 0.05
        if "ocr" in source or "text_content" in source:
            score += 0.05
        if "cloud_" in source:
            score += 0.08
        if "contextual" in source or "llm" in source or is_discovered:
            score -= 0.06
        if is_unknown or "fallback" in source:
            score -= 0.18

        evidence_scores.append(max(0.0, min(1.0, score)))

    evidence_scores.sort(reverse=True)
    primary = evidence_scores[0]
    secondary = evidence_scores[1] if len(evidence_scores) > 1 else 0.0
    tertiary = evidence_scores[2] if len(evidence_scores) > 2 else 0.0

    combined = primary * 0.68 + secondary * 0.22 + tertiary * 0.10
    return max(0.0, min(1.0, combined))


def compute_analysis_decision(
    *,
    visual_score: float,
    audio_score: float,
    disclosure_score: float,
    link_score: float,
    detected_brands: List[Dict[str, Any]] | None,
    disclosure_markers: List[str] | None,
    detected_keywords: List[str] | None,
    has_cta: bool,
    has_commercial_links: bool,
) -> Dict[str, float | bool]:
    brand_signal_score = compute_brand_signal_score(detected_brands)
    has_disclosure = bool(disclosure_markers)
    has_keywords = bool(detected_keywords)

    text_score = max(audio_score, brand_signal_score)
    confidence_score = min(
        1.0,
        visual_score * 0.22
        + audio_score * 0.18
        + text_score * 0.28
        + disclosure_score * 0.14
        + link_score * 0.18,
    )

    support_signals = sum(
        [
            visual_score >= 0.45,
            audio_score >= 0.35 or has_keywords,
            brand_signal_score >= 0.42,
            disclosure_score >= 0.45 or has_disclosure,
            link_score >= 0.45 or has_cta or has_commercial_links,
        ]
    )

    has_advertising = (
        has_disclosure
        or (confidence_score >= 0.58 and support_signals >= 2)
        or (
            (has_cta or has_commercial_links or link_score >= 0.55)
            and (brand_signal_score >= 0.36 or audio_score >= 0.35 or has_keywords)
        )
        or (
            brand_signal_score >= 0.72
            and (visual_score >= 0.45 or audio_score >= 0.32 or has_cta or has_commercial_links)
        )
    )

    return {
        "brand_signal_score": brand_signal_score,
        "text_score": text_score,
        "confidence_score": confidence_score,
        "has_advertising": has_advertising,
        "support_signals": float(support_signals),
    }


def classify_advertising(
    has_advertising: bool,
    disclosure_markers: List[str] | None,
    detected_brands: List[Dict[str, Any]] | None,
    detected_keywords: List[str] | None,
    has_cta: bool = False,
    has_commercial_links: bool = False,
    commercial_urls: List[str] | None = None,
) -> Dict[str, str]:
    disclosure_markers = disclosure_markers or []
    detected_brands = detected_brands or []
    detected_keywords = detected_keywords or []
    commercial_urls = commercial_urls or []

    has_disclosure = len(disclosure_markers) > 0
    has_mentions = len(detected_brands) > 0 or len(detected_keywords) > 0
    strong_brand_signal = compute_brand_signal_score(detected_brands) >= 0.55

    if has_disclosure:
        return {
            "classification": "official",
            "reason": "Disclosure markers detected (e.g. ERID/#ad/#реклама).",
        }

    if has_advertising and (has_cta or has_commercial_links):
        urls_text = f" Links: {', '.join(commercial_urls[:2])}" if commercial_urls else ""
        return {
            "classification": "hidden_ad",
            "reason": f"Potential hidden advertising detected. CTA: {has_cta}, Commercial links: {has_commercial_links}.{urls_text}",
        }

    if has_advertising and strong_brand_signal:
        return {
            "classification": "unofficial",
            "reason": "Consistent brand evidence detected without official disclosure.",
        }

    if has_advertising:
        return {
            "classification": "unofficial",
            "reason": "Advertising signals detected without official disclosure.",
        }

    if has_mentions:
        return {
            "classification": "mention",
            "reason": "Brand mention detected without enough advertising evidence.",
        }

    if has_cta or has_commercial_links:
        urls_text = f" Links: {', '.join(commercial_urls[:2])}" if commercial_urls else ""
        return {
            "classification": "potential_ad",
            "reason": f"Call-to-action or commercial links detected.{urls_text}",
        }

    return {
        "classification": "no_ad",
        "reason": "No advertising signals detected.",
    }
