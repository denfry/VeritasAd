from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .fetchers.ytdlp_fetcher import YtDlpFetcher
from .labeler import build_weak_label
from .manifest import append_entries, existing_ids, load_manifest, stats
from .schema import ManifestEntry


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_sources(path: Path) -> list[str]:
    urls: list[str] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("{"):
                urls.append(str(json.loads(line)["url"]))
            else:
                urls.append(line)
    return urls


def run(sources: Path, manifest: Path, fetcher=None) -> dict:
    fetcher = fetcher or YtDlpFetcher(_now_iso())
    done = existing_ids(manifest)
    new_entries: list[ManifestEntry] = []
    for url in read_sources(sources):
        try:
            record = fetcher.fetch(url)
        except Exception as exc:  # one bad video must not abort the harvest
            print(f"[skip] {url}: {exc}", file=sys.stderr)
            continue
        if not record.video_id or record.video_id in done:
            continue
        label = build_weak_label(record)
        new_entries.append(ManifestEntry(record=record, label=label))
        done.add(record.video_id)
    append_entries(manifest, new_entries)
    return stats(load_manifest(manifest))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="VeritasAd corpus harvester + ERID weak-label miner",
    )
    parser.add_argument("--sources", required=True, type=Path,
                        help="JSONL/text file of video URLs to harvest")
    parser.add_argument("--manifest", required=True, type=Path,
                        help="output JSONL manifest (appended, resumable)")
    args = parser.parse_args(argv)
    result = run(args.sources, args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
