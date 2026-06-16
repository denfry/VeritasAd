from corpus.cli import run
from corpus.schema import Platform, VideoRecord, WeakLabelClass


class FakeFetcher:
    def __init__(self, mapping):
        self._mapping = mapping

    def fetch(self, url):
        if url not in self._mapping:
            raise RuntimeError(f"not found: {url}")
        return self._mapping[url]


def _sources_file(tmp_path, urls):
    path = tmp_path / "sources.jsonl"
    path.write_text("\n".join(urls) + "\n", encoding="utf-8")
    return path


def _records():
    ad = VideoRecord(video_id="ad1", platform=Platform.YOUTUBE,
                     url="https://y/AD",
                     description="erid: 2Vfnxw9ab на правах рекламы")
    clean = VideoRecord(video_id="cl1", platform=Platform.VK,
                        url="https://v/CLEAN", description="просто влог")
    return ad, clean


def test_run_builds_manifest_with_mixed_labels(tmp_path):
    ad, clean = _records()
    sources = _sources_file(tmp_path, [
        '{"url": "https://y/AD"}',
        '{"url": "https://v/CLEAN"}',
        '{"url": "https://y/BROKEN"}',  # raises -> skipped, run continues
    ])
    manifest = tmp_path / "manifest.jsonl"
    fetcher = FakeFetcher({"https://y/AD": ad, "https://v/CLEAN": clean})

    result = run(sources, manifest, fetcher=fetcher)

    assert result["total"] == 2
    assert result["by_label"] == {"disclosed_ad": 1, "unlabeled": 1}


def test_run_is_resumable_and_skips_known_ids(tmp_path):
    ad, clean = _records()
    sources = _sources_file(tmp_path, ['{"url": "https://y/AD"}',
                                       '{"url": "https://v/CLEAN"}'])
    manifest = tmp_path / "manifest.jsonl"
    fetcher = FakeFetcher({"https://y/AD": ad, "https://v/CLEAN": clean})

    run(sources, manifest, fetcher=fetcher)
    result = run(sources, manifest, fetcher=fetcher)  # second pass

    assert result["total"] == 2  # no duplicates appended


def test_run_accepts_bare_url_lines_and_comments(tmp_path):
    ad, _ = _records()
    sources = _sources_file(tmp_path, ["# seed list", "https://y/AD"])
    manifest = tmp_path / "manifest.jsonl"
    result = run(sources, manifest, fetcher=FakeFetcher({"https://y/AD": ad}))
    assert result["total"] == 1
