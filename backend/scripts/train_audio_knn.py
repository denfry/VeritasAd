"""Train the MFCC + KNN acoustic ad-window classifier (thesis sec. 3.2).

Reads a manifest of labelled audio clips, extracts 40-dim MFCC feature vectors
over 2-second windows (50% overlap) at 16 kHz, fits a
``KNeighborsClassifier(n_neighbors=5)`` and serialises it to
``models/audio_knn.joblib`` (configurable via ``AUDIO_KNN_MODEL_PATH``).

Manifest format (CSV, header required)::

    path,label
    data/audio/ad_001.wav,1
    data/audio/clean_001.wav,0

where ``label`` is 1 for advertising audio and 0 otherwise. Paths may be audio
or video files (audio is extracted on the fly).

Usage::

    python -m scripts.train_audio_knn --manifest data/audio/manifest.csv \
        --output models/audio_knn.joblib
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

# Allow running both as a module and as a script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.services.audio_analyzer import AudioAnalyzer  # noqa: E402


def _load_windows(analyzer: AudioAnalyzer, media_path: Path) -> np.ndarray:
    """Return MFCC windows for an audio or video file."""
    if media_path.suffix.lower() in {".wav", ".mp3", ".m4a", ".flac", ".ogg"}:
        return analyzer.extract_mfcc_windows(media_path)
    # Treat as video: extract audio first.
    audio_path = analyzer.extract_audio(media_path)
    if not audio_path or not audio_path.exists():
        return np.empty((0, settings.AUDIO_MFCC_COUNT))
    try:
        return analyzer.extract_mfcc_windows(audio_path)
    finally:
        try:
            audio_path.unlink()
        except Exception:
            pass


def build_dataset(manifest: Path) -> tuple[np.ndarray, np.ndarray]:
    analyzer = AudioAnalyzer()
    features: list[np.ndarray] = []
    labels: list[int] = []

    with open(manifest, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            media_path = Path(row["path"])
            if not media_path.is_absolute():
                media_path = manifest.parent / media_path
            label = int(row["label"])
            windows = _load_windows(analyzer, media_path)
            if windows.shape[0] == 0:
                print(f"  ! no windows extracted for {media_path}")
                continue
            features.append(windows)
            labels.extend([label] * windows.shape[0])
            print(f"  + {media_path.name}: {windows.shape[0]} windows (label={label})")

    if not features:
        raise SystemExit("No features extracted; check the manifest paths.")

    X = np.vstack(features)
    y = np.asarray(labels, dtype=int)
    return X, y


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="CSV manifest path,label")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(settings.AUDIO_KNN_MODEL_PATH or "models/audio_knn.joblib"),
    )
    parser.add_argument("--neighbors", type=int, default=settings.AUDIO_KNN_NEIGHBORS)
    args = parser.parse_args()

    import joblib
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import cross_val_score

    print(f"Building dataset from {args.manifest} ...")
    X, y = build_dataset(args.manifest)
    print(f"Dataset: {X.shape[0]} windows, {X.shape[1]} features, "
          f"{int((y == 1).sum())} ad / {int((y == 0).sum())} non-ad")

    clf = KNeighborsClassifier(n_neighbors=args.neighbors)

    if len(np.unique(y)) > 1 and X.shape[0] >= args.neighbors * 2:
        scores = cross_val_score(clf, X, y, cv=min(5, X.shape[0] // args.neighbors))
        print(f"Cross-val accuracy: {scores.mean():.3f} +/- {scores.std():.3f}")

    clf.fit(X, y)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, args.output)
    print(f"Saved KNN model -> {args.output}")


if __name__ == "__main__":
    main()
