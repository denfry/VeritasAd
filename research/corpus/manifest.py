from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .schema import (
    SCHEMA_VERSION,
    ManifestEntry,
    entry_from_dict,
    entry_to_dict,
)


def append_entries(path: Path, entries: list[ManifestEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry_to_dict(entry), ensure_ascii=False) + "\n")


def load_manifest(path: Path) -> list[ManifestEntry]:
    if not path.exists():
        return []
    out: list[ManifestEntry] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(entry_from_dict(json.loads(line)))
    return out


def existing_ids(path: Path) -> set[str]:
    return {entry.record.video_id for entry in load_manifest(path)}


def stats(entries: list[ManifestEntry]) -> dict:
    by_label = Counter(entry.label.label.value for entry in entries)
    by_platform = Counter(entry.record.platform.value for entry in entries)
    return {
        "total": len(entries),
        "by_label": dict(by_label),
        "by_platform": dict(by_platform),
        "schema_version": SCHEMA_VERSION,
    }
