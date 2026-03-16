#!/bin/sh
set -eu

INTERVAL_SECONDS="${YTDLP_COOKIES_REFRESH_INTERVAL_SECONDS:-43200}"

echo "Starting YouTube cookies refresh loop, interval=${INTERVAL_SECONDS}s"

while true; do
  python /app/scripts/refresh_youtube_cookies.py || true
  sleep "${INTERVAL_SECONDS}"
done
