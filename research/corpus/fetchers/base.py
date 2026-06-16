from __future__ import annotations

from typing import Protocol

from ..schema import VideoRecord


class MetadataFetcher(Protocol):
    def fetch(self, url: str) -> VideoRecord:
        """Fetch metadata for a single video URL."""
        ...
