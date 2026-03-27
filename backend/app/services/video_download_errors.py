"""Helpers to map low-level downloader errors to user-friendly messages."""
from __future__ import annotations

from typing import Dict

from app.core.errors import ErrorCode


def classify_processing_error(error_text: str) -> Dict[str, str]:
    """
    Convert raw downloader/runtime errors to a stable user-facing message + code.

    Returns dict with keys:
    - error_code
    - user_message
    """
    raw = (error_text or "").strip()
    low = raw.lower()

    # YouTube anti-bot / auth required
    if (
        "sign in to confirm" in low
        and "not a bot" in low
        and ("youtube" in low or "yt-dlp" in low)
    ):
        return {
            "error_code": ErrorCode.VIDEO_DOWNLOAD_FAILED,
            "user_message": (
                "Could not fetch this YouTube video due to platform protection. "
                "Please try again later or upload the video file directly."
            ),
        }

    # Private / unavailable content
    if any(
        marker in low
        for marker in [
            "private video",
            "video unavailable",
            "members-only",
            "this video is unavailable",
            "requested format is not available",
        ]
    ):
        return {
            "error_code": ErrorCode.VIDEO_DOWNLOAD_FAILED,
            "user_message": (
                "Video is not available for download (private, removed, or restricted). "
                "Check the link or upload the file manually."
            ),
        }

    # Network and timeout failures
    if any(
        marker in low
        for marker in [
            "timed out",
            "timeout",
            "network is unreachable",
            "temporary failure in name resolution",
            "connection reset",
            "http error 429",
            "http error 403",
            "too many requests",
            "fragment not found",
            "the downloaded file is empty",
            "forbidden",
        ]
    ):
        return {
            "error_code": ErrorCode.VIDEO_DOWNLOAD_FAILED,
            "user_message": (
                "Service could not download the video due to a temporary platform or network limitation. "
                "Please retry later."
            ),
        }

    return {
        "error_code": ErrorCode.PROCESSING_FAILED,
        "user_message": "Could not process the video. Please retry later.",
    }
