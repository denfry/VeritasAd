#!/usr/bin/env python3
"""Refresh server-side YouTube cookies file for yt-dlp."""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path


LOGGER = logging.getLogger("yt_cookies_refresh")


def _run(cmd: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _looks_like_netscape_cookie_file(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            sample = f.read(4096)
        return "netscape http cookie file" in sample.lower() or "\t" in sample
    except Exception:
        return False


def _probe_cookie_access(cookies_file: Path, probe_url: str) -> bool:
    cmd = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--cookies",
        str(cookies_file),
        "--skip-download",
        "--simulate",
        "--no-playlist",
        "--no-warnings",
        probe_url,
    ]
    result = _run(cmd, timeout=180)
    if result.returncode == 0:
        return True
    combined = f"{result.stdout}\n{result.stderr}".lower()
    if "sign in to confirm" in combined and "not a bot" in combined:
        return False
    return False


def main() -> int:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    target = Path(os.getenv("YTDLP_COOKIES_FILE", "/app/data/cookies/youtube_cookies.txt"))
    source_file = os.getenv("YTDLP_COOKIES_SOURCE_FILE", "").strip()
    browser = os.getenv("YTDLP_COOKIES_FROM_BROWSER", "").strip()
    probe_url = os.getenv(
        "YTDLP_COOKIES_PROBE_URL",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ).strip()

    target.parent.mkdir(parents=True, exist_ok=True)
    previous_backup = target.with_suffix(".bak")

    if target.exists():
        shutil.copy2(target, previous_backup)

    refreshed = False

    if source_file:
        src = Path(source_file)
        if src.exists():
            shutil.copy2(src, target)
            refreshed = True
            LOGGER.info("cookies_refreshed_from_source_file source=%s target=%s", src, target)
        else:
            LOGGER.warning("cookies_source_file_missing source=%s", src)

    if not refreshed and browser:
        cmd = [
            sys.executable,
            "-m",
            "yt_dlp",
            "--cookies-from-browser",
            browser,
            "--cookies",
            str(target),
            "--skip-download",
            "--simulate",
            "--no-playlist",
            "--no-warnings",
            probe_url,
        ]
        result = _run(cmd, timeout=180)
        if result.returncode == 0 and _looks_like_netscape_cookie_file(target):
            refreshed = True
            LOGGER.info("cookies_refreshed_from_browser browser=%s target=%s", browser, target)
        else:
            LOGGER.warning(
                "cookies_refresh_from_browser_failed browser=%s code=%s stderr_tail=%s",
                browser,
                result.returncode,
                "\n".join((result.stderr or "").splitlines()[-4:]),
            )

    if not _looks_like_netscape_cookie_file(target):
        if previous_backup.exists():
            shutil.copy2(previous_backup, target)
            LOGGER.warning("cookies_file_invalid_restored_backup target=%s", target)
        else:
            LOGGER.error("cookies_file_invalid_and_no_backup target=%s", target)
            return 1

    if not _probe_cookie_access(target, probe_url):
        LOGGER.warning("cookies_probe_failed target=%s probe_url=%s", target, probe_url)
        if previous_backup.exists():
            shutil.copy2(previous_backup, target)
            LOGGER.warning("cookies_probe_failed_restored_backup target=%s", target)
            if _probe_cookie_access(target, probe_url):
                LOGGER.info("backup_cookies_probe_ok target=%s", target)
                return 0
        return 1

    LOGGER.info("cookies_ready target=%s", target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
