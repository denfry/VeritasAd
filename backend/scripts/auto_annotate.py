from __future__ import annotations

import argparse
import asyncio
import csv
import json
import logging
import math
import sys
import time
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
from yt_dlp import YoutubeDL

BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import settings
from app.services.disclosure_detector import DisclosureDetector
from app.services.link_detector import LinkDetector
from app.services.video_processor import VideoProcessor
from app.utils.ad_classification import (
    classify_advertising,
    compute_analysis_decision,
    merge_brand_detections,
)

logger = logging.getLogger("auto_annotate")

DEFAULT_VIDEO_QUERIES = [
    "sponsored review promo code",
    "affiliate review partner discount",
    "brand integration ad read",
    "обзор промокод реклама",
    "спонсор интеграция скидка",
    "партнерский материал бренд",
    "tech review unboxing",
    "gaming highlights stream",
    "news analysis today",
    "tutorial how to build",
]

DEFAULT_TELEGRAM_CHANNELS = [
    "banksta",
    "meduzalive",
    "rozetked",
    "vcnews",
    "tproger",
    "thevillage",
    "durov",
]

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "annotated" / "auto_dataset"
DEFAULT_LOCAL_VIDEO_DIR = PROJECT_ROOT / "data" / "uploads"
JSONL_FILENAME = "dataset.jsonl"
CSV_FILENAME = "dataset.csv"
SOURCES_FILENAME = "sources.json"
SUMMARY_FILENAME = "summary.md"


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")


def infer_source_type(url: str | None) -> str:
    if not url:
        return "file"

    lowered = url.lower()
    if "youtu.be" in lowered or "youtube.com" in lowered:
        return "youtube"
    if "t.me" in lowered or "telegram" in lowered:
        return "telegram"
    if "instagram.com" in lowered or "instagr.am" in lowered:
        return "instagram"
    if "vk.com" in lowered or "vk.ru" in lowered:
        return "vk"
    if "tiktok.com" in lowered:
        return "tiktok"
    return "url"


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{parsed.scheme}://{parsed.netloc}{path}{query}"


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def unique_by(items: Iterable[dict[str, Any]], key_name: str) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = str(item.get(key_name, "")).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def collect_local_videos(directory: Path, limit: int) -> list[dict[str, Any]]:
    if limit <= 0 or not directory.exists():
        return []

    allowed_exts = {ext.lower() for ext in settings.ALLOWED_VIDEO_EXTENSIONS}
    collected: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*")):
        if path.is_file() and path.suffix.lower() in allowed_exts:
            collected.append(
                {
                    "content_type": "video",
                    "source_type": "file",
                    "source_key": str(path.resolve()),
                    "source_file": str(path.resolve()),
                    "title": path.stem,
                    "origin": "local_directory",
                }
            )
        if len(collected) >= limit:
            break
    return collected


def search_youtube_urls(query: str, limit: int) -> list[dict[str, Any]]:
    search_term = f"ytsearchdate{limit}:{query}"
    options = {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "noplaylist": True,
        "ignoreerrors": True,
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(search_term, download=False) or {}

    results: list[dict[str, Any]] = []
    for entry in info.get("entries", []) or []:
        url = entry.get("url") or entry.get("webpage_url")
        if not url:
            continue
        if not str(url).startswith("http"):
            entry_id = entry.get("id")
            if entry_id:
                url = f"https://www.youtube.com/watch?v={entry_id}"
        if not str(url).startswith("http"):
            continue

        normalized = normalize_url(str(url))
        results.append(
            {
                "content_type": "video",
                "source_type": "youtube",
                "source_url": normalized,
                "source_key": normalized,
                "title": entry.get("title") or "",
                "origin": "youtube_search",
                "query": query,
            }
        )
    return results


def collect_youtube_videos(
    target_count: int,
    queries: list[str],
    url_file: Path | None,
    include_local_dir: Path | None,
) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []

    if include_local_dir:
        local_limit = min(target_count, 25)
        collected.extend(collect_local_videos(include_local_dir, local_limit))

    if url_file and url_file.exists():
        for url in read_lines(url_file):
            normalized = normalize_url(url)
            collected.append(
                {
                    "content_type": "video",
                    "source_type": infer_source_type(normalized),
                    "source_url": normalized,
                    "source_key": normalized,
                    "title": "",
                    "origin": "video_url_file",
                }
            )

    if len(unique_by(collected, "source_key")) >= target_count:
        return unique_by(collected, "source_key")[:target_count]

    if not queries:
        queries = DEFAULT_VIDEO_QUERIES[:]

    remaining = max(target_count - len(unique_by(collected, "source_key")), 0)
    per_query = max(6, math.ceil((remaining * 1.4) / max(len(queries), 1)))

    for query in queries:
        try:
            collected.extend(search_youtube_urls(query, per_query))
        except Exception as exc:
            logger.warning("youtube_search_failed query=%s error=%s", query, exc)
        deduped = unique_by(collected, "source_key")
        if len(deduped) >= target_count:
            return deduped[:target_count]

    return unique_by(collected, "source_key")[:target_count]


def extract_archive_urls(
    channel: str,
    html: str,
) -> tuple[list[str], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    urls: list[str] = []
    for anchor in soup.select("a.tgme_widget_message_date[href]"):
        href = anchor.get("href", "").strip()
        if href.startswith("https://t.me/"):
            urls.append(normalize_url(href))

    next_url: str | None = None
    archive_prefix = f"/s/{channel}?before="
    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "").strip()
        if href.startswith(archive_prefix):
            next_url = f"https://t.me{href}"
            break

    return urls, next_url


def collect_telegram_posts_from_channel(channel: str, limit: int) -> list[dict[str, Any]]:
    headers = {"User-Agent": "Mozilla/5.0"}
    client = httpx.Client(timeout=20, headers=headers, follow_redirects=True)
    collected: list[dict[str, Any]] = []
    seen: set[str] = set()
    next_url: str | None = f"https://t.me/s/{channel}"

    try:
        while next_url and len(collected) < limit:
            response = client.get(next_url)
            response.raise_for_status()
            urls, next_url = extract_archive_urls(channel, response.text)
            page_added = 0
            for url in urls:
                if url in seen:
                    continue
                seen.add(url)
                collected.append(
                    {
                        "content_type": "post",
                        "source_type": "telegram",
                        "source_url": url,
                        "source_key": url,
                        "origin": "telegram_archive",
                        "channel": channel,
                    }
                )
                page_added += 1
                if len(collected) >= limit:
                    break
            if page_added == 0:
                break
    finally:
        client.close()

    return collected


def collect_posts(
    target_count: int,
    channels: list[str],
    url_file: Path | None,
) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []

    if url_file and url_file.exists():
        for url in read_lines(url_file):
            normalized = normalize_url(url)
            collected.append(
                {
                    "content_type": "post",
                    "source_type": infer_source_type(normalized),
                    "source_url": normalized,
                    "source_key": normalized,
                    "origin": "post_url_file",
                }
            )

    if len(unique_by(collected, "source_key")) >= target_count:
        return unique_by(collected, "source_key")[:target_count]

    if not channels:
        channels = DEFAULT_TELEGRAM_CHANNELS[:]

    remaining = max(target_count - len(unique_by(collected, "source_key")), 0)
    per_channel = max(20, math.ceil((remaining * 1.2) / max(len(channels), 1)))

    for channel in channels:
        try:
            collected.extend(collect_telegram_posts_from_channel(channel, per_channel))
        except Exception as exc:
            logger.warning("telegram_archive_failed channel=%s error=%s", channel, exc)
        deduped = unique_by(collected, "source_key")
        if len(deduped) >= target_count:
            return deduped[:target_count]

    return unique_by(collected, "source_key")[:target_count]


async def analyze_post_source(
    source: dict[str, Any],
    processor: VideoProcessor,
    disclosure_detector: DisclosureDetector,
) -> dict[str, Any]:
    started_at = time.time()
    url = str(source["source_url"])
    metadata = await processor.get_url_metadata(url)
    title = str(metadata.get("title") or "")
    description = str(metadata.get("description") or "")
    uploader = str(metadata.get("uploader") or "")
    text_content = f"{title} {description}".strip()

    disclosure = await disclosure_detector.analyze(
        text=description,
        description=title,
        plan="free",
    )
    link_result = LinkDetector().analyze(text=text_content, description=description)
    disclosure_markers = disclosure.get("markers", []) or []
    discovered_brands = [
        {
            "name": brand["name"],
            "confidence": brand["confidence"],
            "source": brand["source"],
            "is_discovered": True,
        }
        for brand in disclosure.get("discovered_brands", []) or []
    ]
    detected_brands = merge_brand_detections(
        processor.detect_brands_in_text(text_content),
        discovered_brands,
    )

    decision = compute_analysis_decision(
        visual_score=0.0,
        audio_score=0.0,
        disclosure_score=float(disclosure.get("score", 0.0)),
        link_score=float(link_result.get("link_score", 0.0)),
        detected_brands=detected_brands,
        disclosure_markers=disclosure_markers,
        detected_keywords=[],
        has_cta=bool(link_result.get("has_cta", False)),
        has_commercial_links=bool(link_result.get("has_ad_signals", False)),
    )
    has_advertising = bool(decision["has_advertising"]) or bool(disclosure_markers)
    classification = classify_advertising(
        has_advertising=has_advertising,
        disclosure_markers=disclosure_markers,
        detected_brands=detected_brands,
        detected_keywords=[],
        has_cta=bool(link_result.get("has_cta", False)),
        has_commercial_links=bool(link_result.get("has_ad_signals", False)),
        commercial_urls=link_result.get("urls", []),
    )

    return {
        "status": "completed",
        "content_type": "post",
        "source_type": source["source_type"],
        "source_url": url,
        "source_file": "",
        "source_key": source["source_key"],
        "source_origin": source.get("origin", ""),
        "source_channel": source.get("channel", ""),
        "query": source.get("query", ""),
        "title": title,
        "uploader": uploader,
        "duration": metadata.get("duration"),
        "has_advertising": has_advertising,
        "confidence_score": float(decision["confidence_score"]),
        "visual_score": 0.0,
        "audio_score": 0.0,
        "text_score": float(decision["text_score"]),
        "disclosure_score": float(disclosure.get("score", 0.0)),
        "link_score": float(link_result.get("link_score", 0.0)),
        "ad_classification": classification["classification"],
        "ad_reason": classification["reason"],
        "detected_brands": detected_brands,
        "detected_keywords": [],
        "disclosure_text": disclosure_markers,
        "cta_matches": link_result.get("cta_matches", []),
        "commercial_urls": link_result.get("urls", []),
        "transcript": "",
        "description": description,
        "processing_time": round(time.time() - started_at, 2),
        "error": "",
    }


async def analyze_video_source(
    source: dict[str, Any],
    processor: VideoProcessor,
) -> dict[str, Any]:
    started_at = time.time()
    if source["source_type"] == "file":
        file_path = Path(str(source["source_file"]))
        with file_path.open("rb") as handle:
            upload = SimpleNamespace(file=handle, filename=file_path.name, size=file_path.stat().st_size)
            result = await processor.process(file=upload)
        title = source.get("title", file_path.stem)
        uploader = ""
        source_url = ""
        source_file = str(file_path.resolve())
    else:
        source_url = str(source["source_url"])
        metadata = await processor.get_url_metadata(source_url)
        result = await processor.process(url=source_url)
        title = metadata.get("title") or source.get("title", "")
        uploader = metadata.get("uploader") or ""
        source_file = ""

    status = str(result.get("status", "failed"))
    return {
        "status": status,
        "content_type": "video",
        "source_type": source["source_type"],
        "source_url": source_url,
        "source_file": source_file,
        "source_key": source["source_key"],
        "source_origin": source.get("origin", ""),
        "source_channel": source.get("channel", ""),
        "query": source.get("query", ""),
        "title": title,
        "uploader": uploader,
        "duration": result.get("duration"),
        "has_advertising": bool(result.get("has_advertising", False)),
        "confidence_score": float(result.get("confidence_score", 0.0) or 0.0),
        "visual_score": float(result.get("visual_score", 0.0) or 0.0),
        "audio_score": float(result.get("audio_score", 0.0) or 0.0),
        "text_score": float(result.get("text_score", 0.0) or 0.0),
        "disclosure_score": float(result.get("disclosure_score", 0.0) or 0.0),
        "link_score": float(result.get("link_score", 0.0) or 0.0),
        "ad_classification": result.get("ad_classification") or "",
        "ad_reason": result.get("ad_reason") or result.get("error") or "",
        "detected_brands": result.get("detected_brands", []),
        "detected_keywords": result.get("detected_keywords", []),
        "disclosure_text": result.get("disclosure_text", []),
        "cta_matches": result.get("cta_matches", []),
        "commercial_urls": result.get("commercial_urls", []),
        "transcript": result.get("transcript", ""),
        "description": "",
        "processing_time": round(float(result.get("processing_time", 0.0) or 0.0), 2),
        "error": "" if status == "completed" else str(result.get("error", "Unknown error")),
        "video_id": result.get("video_id", ""),
        "file_path": result.get("file_path", ""),
        "elapsed_wall_time": round(time.time() - started_at, 2),
    }


def finalize_record(record: dict[str, Any], review_threshold: float) -> dict[str, Any]:
    confidence = float(record.get("confidence_score", 0.0) or 0.0)
    needs_review = record.get("status") != "completed" or confidence < review_threshold
    brand_names = [brand.get("name", "") for brand in record.get("detected_brands", []) if brand.get("name")]
    record["record_id"] = f"{record['content_type']}::{record['source_key']}"
    record["annotation_source"] = "veritasad_auto"
    record["needs_review"] = needs_review
    record["review_reason"] = (
        "analysis_failed"
        if record.get("status") != "completed"
        else "low_confidence"
        if confidence < review_threshold
        else ""
    )
    record["brand_names"] = brand_names
    return record


def flatten_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": record.get("record_id", ""),
        "status": record.get("status", ""),
        "content_type": record.get("content_type", ""),
        "source_type": record.get("source_type", ""),
        "source_origin": record.get("source_origin", ""),
        "source_channel": record.get("source_channel", ""),
        "query": record.get("query", ""),
        "source_url": record.get("source_url", ""),
        "source_file": record.get("source_file", ""),
        "title": record.get("title", ""),
        "uploader": record.get("uploader", ""),
        "duration": record.get("duration", ""),
        "has_advertising": record.get("has_advertising", False),
        "confidence_score": record.get("confidence_score", 0.0),
        "ad_classification": record.get("ad_classification", ""),
        "ad_reason": record.get("ad_reason", ""),
        "visual_score": record.get("visual_score", 0.0),
        "audio_score": record.get("audio_score", 0.0),
        "text_score": record.get("text_score", 0.0),
        "disclosure_score": record.get("disclosure_score", 0.0),
        "link_score": record.get("link_score", 0.0),
        "brand_names": "; ".join(record.get("brand_names", [])),
        "detected_brands_json": json.dumps(record.get("detected_brands", []), ensure_ascii=False),
        "detected_keywords": "; ".join(record.get("detected_keywords", [])),
        "disclosure_text": "; ".join(record.get("disclosure_text", [])),
        "cta_matches": "; ".join(record.get("cta_matches", [])),
        "commercial_urls": "; ".join(record.get("commercial_urls", [])),
        "transcript_preview": str(record.get("transcript", ""))[:500],
        "description_preview": str(record.get("description", ""))[:500],
        "processing_time": record.get("processing_time", ""),
        "needs_review": record.get("needs_review", False),
        "review_reason": record.get("review_reason", ""),
        "annotation_source": record.get("annotation_source", ""),
        "error": record.get("error", ""),
    }


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    rows = [flatten_record(record) for record in records]
    fieldnames = list(rows[0].keys()) if rows else list(flatten_record({}).keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_summary(records: list[dict[str, Any]], sources: dict[str, Any]) -> str:
    total = len(records)
    completed = sum(1 for record in records if record.get("status") == "completed")
    failed = total - completed
    ads = sum(1 for record in records if record.get("has_advertising"))
    needs_review = sum(1 for record in records if record.get("needs_review"))

    type_counts = Counter(record.get("content_type", "unknown") for record in records)
    source_counts = Counter(record.get("source_type", "unknown") for record in records)
    brand_counts = Counter()
    for record in records:
        brand_counts.update(record.get("brand_names", []))

    lines = [
        "# Auto-Annotated Dataset",
        "",
        "## Totals",
        f"- Total records: {total}",
        f"- Completed: {completed}",
        f"- Failed: {failed}",
        f"- With advertising: {ads}",
        f"- Needs review: {needs_review}",
        "",
        "## Composition",
    ]

    for content_type, count in sorted(type_counts.items()):
        lines.append(f"- {content_type}: {count}")

    lines.extend(["", "## Sources"])
    for source_type, count in sorted(source_counts.items()):
        lines.append(f"- {source_type}: {count}")

    lines.extend(["", "## Top Brands"])
    if brand_counts:
        for name, count in brand_counts.most_common(15):
            lines.append(f"- {name}: {count}")
    else:
        lines.append("- No brands detected yet")

    lines.extend(
        [
            "",
            "## Provenance",
            f"- Video queries: {', '.join(sources.get('video_queries', [])) or 'none'}",
            f"- Telegram channels: {', '.join(sources.get('telegram_channels', [])) or 'none'}",
            f"- Generated at output dir: {sources.get('output_dir', '')}",
            "",
            "## Note",
            "- Labels are model-generated and should be reviewed where confidence is low.",
        ]
    )
    return "\n".join(lines) + "\n"


async def run(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = output_dir / JSONL_FILENAME
    csv_path = output_dir / CSV_FILENAME
    summary_path = output_dir / SUMMARY_FILENAME
    sources_path = output_dir / SOURCES_FILENAME

    existing_records = load_jsonl(jsonl_path) if args.resume else []
    completed_keys = {record.get("source_key", "") for record in existing_records}

    video_queries = args.video_query or DEFAULT_VIDEO_QUERIES[:]
    telegram_channels = args.telegram_channel or DEFAULT_TELEGRAM_CHANNELS[:]
    local_video_dir = Path(args.local_video_dir).resolve() if args.local_video_dir else None
    video_url_file = Path(args.video_url_file).resolve() if args.video_url_file else None
    post_url_file = Path(args.post_url_file).resolve() if args.post_url_file else None

    logger.info("collecting_sources")
    video_sources = collect_youtube_videos(
        target_count=args.target_videos,
        queries=video_queries,
        url_file=video_url_file,
        include_local_dir=local_video_dir,
    )
    post_sources = collect_posts(
        target_count=args.target_posts,
        channels=telegram_channels,
        url_file=post_url_file,
    )

    selected_sources = video_sources + post_sources
    selected_sources = [source for source in selected_sources if source["source_key"] not in completed_keys]

    sources_manifest = {
        "output_dir": str(output_dir),
        "target_videos": args.target_videos,
        "target_posts": args.target_posts,
        "video_queries": video_queries,
        "telegram_channels": telegram_channels,
        "queued_sources": selected_sources,
        "resume": args.resume,
    }
    sources_path.write_text(json.dumps(sources_manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info(
        "starting_analysis queued_videos=%s queued_posts=%s resume=%s",
        sum(1 for source in selected_sources if source["content_type"] == "video"),
        sum(1 for source in selected_sources if source["content_type"] == "post"),
        args.resume,
    )

    processor = VideoProcessor(use_llm=False)
    disclosure_detector = DisclosureDetector(use_llm=False)
    all_records = existing_records[:]

    for index, source in enumerate(selected_sources, start=1):
        logger.info(
            "analyzing_item index=%s total=%s type=%s source=%s",
            index,
            len(selected_sources),
            source["content_type"],
            source["source_key"],
        )
        try:
            if source["content_type"] == "post":
                record = await analyze_post_source(source, processor, disclosure_detector)
            else:
                record = await analyze_video_source(source, processor)
        except Exception as exc:
            logger.exception("analysis_crashed source=%s", source["source_key"])
            record = {
                "status": "failed",
                "content_type": source["content_type"],
                "source_type": source["source_type"],
                "source_url": source.get("source_url", ""),
                "source_file": source.get("source_file", ""),
                "source_key": source["source_key"],
                "source_origin": source.get("origin", ""),
                "source_channel": source.get("channel", ""),
                "query": source.get("query", ""),
                "title": source.get("title", ""),
                "uploader": "",
                "duration": None,
                "has_advertising": False,
                "confidence_score": 0.0,
                "visual_score": 0.0,
                "audio_score": 0.0,
                "text_score": 0.0,
                "disclosure_score": 0.0,
                "link_score": 0.0,
                "ad_classification": "",
                "ad_reason": str(exc),
                "detected_brands": [],
                "detected_keywords": [],
                "disclosure_text": [],
                "cta_matches": [],
                "commercial_urls": [],
                "transcript": "",
                "description": "",
                "processing_time": 0.0,
                "error": str(exc),
            }

        finalized = finalize_record(record, review_threshold=args.review_threshold)
        append_jsonl(jsonl_path, finalized)
        all_records.append(finalized)

    write_csv(csv_path, all_records)
    summary_path.write_text(render_summary(all_records, sources_manifest), encoding="utf-8")

    logger.info(
        "dataset_ready total=%s jsonl=%s csv=%s summary=%s",
        len(all_records),
        jsonl_path,
        csv_path,
        summary_path,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect public sources and auto-annotate them with VeritasAd analysis.",
    )
    parser.add_argument("--target-videos", type=int, default=100, help="Target number of videos")
    parser.add_argument("--target-posts", type=int, default=500, help="Target number of posts")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for JSONL, CSV, sources manifest and summary report",
    )
    parser.add_argument(
        "--local-video-dir",
        default=str(DEFAULT_LOCAL_VIDEO_DIR),
        help="Directory with local videos to include before public URLs",
    )
    parser.add_argument("--video-url-file", help="Optional newline-delimited file with video URLs")
    parser.add_argument("--post-url-file", help="Optional newline-delimited file with post URLs")
    parser.add_argument(
        "--video-query",
        action="append",
        default=[],
        help="YouTube search query. Repeat to add multiple queries.",
    )
    parser.add_argument(
        "--telegram-channel",
        action="append",
        default=[],
        help="Public Telegram channel name for archive scraping. Repeatable.",
    )
    parser.add_argument(
        "--review-threshold",
        type=float,
        default=0.78,
        help="Confidence threshold below which records are flagged for review",
    )
    parser.add_argument(
        "--resume",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Resume from existing dataset.jsonl and skip already analyzed sources",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(args.verbose)
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
