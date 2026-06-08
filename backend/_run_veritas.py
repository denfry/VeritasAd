"""Standalone VeritasAd pipeline runner (no DB/Redis/Celery).

Reproduces the exact detection sequence of `analyze_video_task` on a single
video file and prints a JSON result. Brand/segment timestamps are shifted by
`--offset` seconds so they map back to the original (full) video timeline.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path


def shift(ts_list, offset):
    return [round(float(t) + offset, 2) for t in (ts_list or [])]


async def run(video_path: str, description: str, offset: float, plan: str = "free"):
    from app.services.video_processor import VideoProcessor
    from app.services.link_detector import LinkDetector
    from app.services.aggregator import build_ad_segments
    from app.utils.ad_classification import (
        classify_advertising,
        compute_analysis_decision,
        merge_brand_detections,
    )

    processor = VideoProcessor()
    vp = Path(video_path)

    metadata = await processor.get_video_metadata(vp)

    # --- Visual channel (CLIP / OCR / cloud) ---
    visual_result = await asyncio.to_thread(processor.detect_logos, vp)

    # --- Audio channel (Whisper transcript + keywords + optional MFCC/KNN) ---
    audio_result = await asyncio.to_thread(processor.audio_analyzer.analyze, vp)
    transcript = audio_result.get("transcript", "")

    # --- Disclosure (text) + link channels — use the REAL full description ---
    disclosure_result = await processor.disclosure_detector.analyze(
        text=transcript, description=description, plan=plan
    )
    link_detector = LinkDetector()
    link_result = await asyncio.to_thread(
        link_detector.analyze, text=transcript, description=description
    )

    visual_score = visual_result.get("score", 0.0)
    audio_score = audio_result.get("score", 0.0)
    disclosure_score = disclosure_result.get("score", 0.0)
    disclosure_markers = disclosure_result.get("markers", [])
    link_score = link_result.get("score", 0.0)
    has_cta = disclosure_result.get("has_cta", False)
    has_link_signals = link_result.get("has_ad_signals", False)
    has_disclosure = disclosure_result.get("has_disclosure", False) or bool(disclosure_markers)

    text_detected_brands = processor.detect_brands_in_text(f"{transcript}\n{description}")
    discovered_brands = [
        {
            "name": d["name"],
            "confidence": d["confidence"],
            "source": d["source"],
            "is_discovered": True,
        }
        for d in disclosure_result.get("discovered_brands", [])
    ]
    all_detected_brands = merge_brand_detections(
        visual_result.get("detected_brands", []),
        text_detected_brands,
        discovered_brands,
    )
    all_detected_brands = [
        b for b in all_detected_brands
        if not (
            b.get("is_unknown")
            or "zero_shot" in str(b.get("source", "")).lower()
            or "fallback" in str(b.get("source", "")).lower()
        )
    ]

    ad_segments = build_ad_segments(
        all_detected_brands,
        transcript_segments=audio_result.get("segments", []),
        ad_keywords=processor.audio_analyzer.ad_keywords,
        brand_terms=list(processor.brands) + list(processor.alias_to_brand.keys()),
    )

    decision = compute_analysis_decision(
        visual_score=visual_score,
        audio_score=audio_score,
        disclosure_score=disclosure_score,
        link_score=link_score,
        detected_brands=all_detected_brands,
        disclosure_markers=disclosure_markers,
        detected_keywords=audio_result.get("keywords", []),
        has_cta=has_cta,
        has_commercial_links=has_link_signals,
    )
    confidence_score = float(decision["confidence_score"])
    has_advertising = bool(decision["has_advertising"]) or has_disclosure

    classification = classify_advertising(
        has_advertising=has_advertising,
        disclosure_markers=disclosure_markers,
        detected_brands=all_detected_brands,
        detected_keywords=audio_result.get("keywords", []),
        has_cta=has_cta,
        has_commercial_links=has_link_signals,
        commercial_urls=link_result.get("urls", []),
    )

    # Shift timestamps to absolute video time for comparison with ground truth.
    for b in all_detected_brands:
        b["timestamps_abs"] = shift(b.get("timestamps"), offset)
    ad_segments_abs = [
        {**s, "start": round(s["start"] + offset, 2), "end": round(s["end"] + offset, 2)}
        for s in ad_segments
    ]

    return {
        "clip": video_path,
        "offset": offset,
        "duration": metadata.get("duration"),
        "has_advertising": has_advertising,
        "ad_classification": classification["classification"],
        "ad_reason": classification["reason"],
        "confidence_score": round(confidence_score, 4),
        "scores": {
            "visual": round(float(visual_score), 4),
            "audio": round(float(audio_score), 4),
            "disclosure": round(float(disclosure_score), 4),
            "link": round(float(link_score), 4),
            "text_score": round(float(decision["text_score"]), 4),
            "brand_signal": round(float(decision["brand_signal_score"]), 4),
            "support_signals": decision["support_signals"],
        },
        "detected_brands": [
            {
                "name": b["name"],
                "confidence": round(float(b["confidence"]), 4),
                "source": b["source"],
                "timestamps_abs": b["timestamps_abs"],
            }
            for b in all_detected_brands
        ],
        "ad_segments_abs": ad_segments_abs,
        "detected_keywords": audio_result.get("keywords", []),
        "disclosure_markers": disclosure_markers,
        "erids": disclosure_result.get("erids", []),
        "promo_codes": disclosure_result.get("promo_codes", []),
        "cta_matches": list(set(
            (disclosure_result.get("cta_matches", []) or [])
            + (link_result.get("cta_matches", []) or [])
        )),
        "commercial_urls": link_result.get("urls", []),
        "audio_acoustic_available": audio_result.get("acoustic_available", False),
        "transcript_excerpt": transcript[:600],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--offset", type=float, default=0.0)
    ap.add_argument("--desc-file", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    description = ""
    if args.desc_file:
        description = Path(args.desc_file).read_text(encoding="utf-8", errors="replace")

    result = asyncio.run(run(args.video, description, args.offset))
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(payload, encoding="utf-8")
    # Console may be a non-UTF-8 codepage (cp1251 on Windows); never crash on print.
    sys.stdout.buffer.write(payload.encode("utf-8", errors="replace"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
