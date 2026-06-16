from __future__ import annotations

from typing import Any, Optional

from ..schema import Platform, VideoRecord

_PLATFORM_BY_EXTRACTOR = {
    "youtube": Platform.YOUTUBE,
    "vk": Platform.VK,
    "rutube": Platform.RUTUBE,
}


def platform_from_info(info: dict[str, Any]) -> Platform:
    key = (info.get("extractor_key") or info.get("extractor") or "").lower()
    for needle, platform in _PLATFORM_BY_EXTRACTOR.items():
        if needle in key:
            return platform
    return Platform.UNKNOWN


def _as_float(value: Any) -> Optional[float]:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def parse_ytdlp_info(info: dict[str, Any], fetched_at: str) -> VideoRecord:
    """Pure transform from a yt-dlp info dict to a VideoRecord (no network)."""
    return VideoRecord(
        video_id=str(info.get("id") or ""),
        platform=platform_from_info(info),
        url=info.get("webpage_url") or info.get("original_url") or "",
        title=info.get("title") or "",
        description=info.get("description") or "",
        channel=info.get("channel") or info.get("uploader") or "",
        duration_sec=_as_float(info.get("duration")),
        fetched_at=fetched_at,
    )


class YtDlpFetcher:
    """Live metadata fetch via yt-dlp (YouTube / VK Video / RuTube)."""

    def __init__(self, now_iso: str):
        self._now_iso = now_iso

    def fetch(self, url: str) -> VideoRecord:
        import yt_dlp  # lazy import so unit tests never need the dependency

        opts = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
            "extract_flat": False,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return parse_ytdlp_info(info, self._now_iso)
