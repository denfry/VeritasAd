from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Optional

SCHEMA_VERSION = "1.0"


class Platform(str, Enum):
    YOUTUBE = "youtube"
    VK = "vk"
    RUTUBE = "rutube"
    TELEGRAM = "telegram"
    UNKNOWN = "unknown"


class MarkerType(str, Enum):
    ERID = "erid"                       # strong: legally mandated token
    ADVERTISER_INN = "advertiser_inn"   # strong: "Реклама. Рекламодатель ... ИНН ..."
    HASHTAG_AD = "hashtag_ad"           # strong: #реклама / #ad
    PHRASE_AD = "phrase_ad"             # medium: "на правах рекламы"
    SPONSOR_PHRASE = "sponsor_phrase"   # weak: "при поддержке", "спонсор выпуска"
    PROMO_CODE = "promo_code"           # weak: CTA signal


# Tiers used by the labeler to keep the positive set clean.
STRONG_MARKERS = {
    MarkerType.ERID,
    MarkerType.ADVERTISER_INN,
    MarkerType.HASHTAG_AD,
    MarkerType.PHRASE_AD,
}
WEAK_MARKERS = {MarkerType.SPONSOR_PHRASE, MarkerType.PROMO_CODE}


class WeakLabelClass(str, Enum):
    DISCLOSED_AD = "disclosed_ad"   # positive: legally disclosed advertising
    UNLABELED = "unlabeled"         # unknown: clean OR hidden ad


@dataclass(frozen=True)
class DisclosureMatch:
    marker_type: MarkerType
    matched_text: str
    value: Optional[str] = None
    region_hint_sec: Optional[float] = None


@dataclass
class VideoRecord:
    video_id: str
    platform: Platform
    url: str
    title: str = ""
    description: str = ""
    channel: str = ""
    duration_sec: Optional[float] = None
    fetched_at: str = ""  # ISO8601, supplied by the caller

    def disclosure_text(self) -> str:
        """Text surfaces mined for disclosure markers."""
        return "\n".join(p for p in (self.title, self.description) if p)


@dataclass
class WeakLabel:
    video_id: str
    label: WeakLabelClass
    markers: list[DisclosureMatch] = field(default_factory=list)
    confidence: float = 0.0
    has_weak_signal: bool = False


@dataclass
class ManifestEntry:
    record: VideoRecord
    label: WeakLabel


def entry_to_dict(entry: ManifestEntry) -> dict:
    # str-based enums serialize to their .value via json.dumps.
    return asdict(entry)


def entry_from_dict(d: dict) -> ManifestEntry:
    r = d["record"]
    record = VideoRecord(
        video_id=r["video_id"],
        platform=Platform(r["platform"]),
        url=r["url"],
        title=r.get("title", ""),
        description=r.get("description", ""),
        channel=r.get("channel", ""),
        duration_sec=r.get("duration_sec"),
        fetched_at=r.get("fetched_at", ""),
    )
    lab = d["label"]
    markers = [
        DisclosureMatch(
            marker_type=MarkerType(m["marker_type"]),
            matched_text=m["matched_text"],
            value=m.get("value"),
            region_hint_sec=m.get("region_hint_sec"),
        )
        for m in lab.get("markers", [])
    ]
    label = WeakLabel(
        video_id=lab["video_id"],
        label=WeakLabelClass(lab["label"]),
        markers=markers,
        confidence=lab.get("confidence", 0.0),
        has_weak_signal=lab.get("has_weak_signal", False),
    )
    return ManifestEntry(record=record, label=label)
