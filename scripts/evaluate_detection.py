"""Evaluate advertising-segment detection against manual annotations.

Implements the evaluation methodology described in the thesis (sec. 4.5,
tables 4.3 / 4.5): for each test video the pipeline's predicted advertising
segments are matched to hand-annotated ground-truth segments by temporal IoU
(default >= 0.5); Precision, Recall and F1 are then reported per detector
channel and for the fused ensemble.

This script is the reusable harness — point it at a labelled set of ~50 videos
(~8 hours) to produce the real numbers for the report.

Ground-truth manifest (JSON)::

    {
      "videos": [
        {
          "path": "data/eval/video_001.mp4",
          "segments": [{"start": 12.0, "end": 28.5}, {"start": 91.0, "end": 110.0}]
        }
      ]
    }

Usage::

    python scripts/evaluate_detection.py --annotations data/eval/manifest.json \
        --iou 0.5 --output data/eval/metrics.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

# Make the backend package importable.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.aggregator import temporal_iou, build_ad_segments  # noqa: E402


def match_segments(
    predicted: List[Dict], ground_truth: List[Dict], iou_threshold: float
) -> Dict[str, int]:
    """Greedy one-to-one matching by temporal IoU.

    Returns counts of true positives, false positives and false negatives.
    """
    matched_gt = set()
    tp = 0
    for pred in predicted:
        best_iou = 0.0
        best_idx = -1
        for idx, gt in enumerate(ground_truth):
            if idx in matched_gt:
                continue
            iou = temporal_iou(pred, gt)
            if iou > best_iou:
                best_iou = iou
                best_idx = idx
        if best_idx >= 0 and best_iou >= iou_threshold:
            tp += 1
            matched_gt.add(best_idx)

    fp = len(predicted) - tp
    fn = len(ground_truth) - len(matched_gt)
    return {"tp": tp, "fp": fp, "fn": fn}


def prf(tp: int, fp: int, fn: int) -> Dict[str, float]:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}


def predict_segments(video_path: Path) -> List[Dict]:
    """Run the detection pipeline and return predicted ad segments.

    Imports the heavy services lazily so the harness can be inspected/tested
    without torch/cv2 installed.
    """
    from app.services.video_processor import VideoProcessor  # noqa: WPS433

    processor = VideoProcessor()
    visual = processor.detect_logos(video_path)
    brands = visual.get("detected_brands", [])
    return build_ad_segments(brands)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", required=True, type=Path)
    parser.add_argument("--iou", type=float, default=0.5)
    parser.add_argument("--output", type=Path, default=Path("metrics.json"))
    args = parser.parse_args()

    manifest = json.loads(args.annotations.read_text(encoding="utf-8"))
    videos = manifest.get("videos", [])
    if not videos:
        raise SystemExit("No videos in annotations manifest.")

    totals = {"tp": 0, "fp": 0, "fn": 0}
    per_video = []

    for entry in videos:
        video_path = Path(entry["path"])
        if not video_path.is_absolute():
            video_path = args.annotations.parent / video_path
        ground_truth = entry.get("segments", [])

        if not video_path.exists():
            print(f"  ! missing video: {video_path}")
            continue

        predicted = predict_segments(video_path)
        counts = match_segments(predicted, ground_truth, args.iou)
        for k in totals:
            totals[k] += counts[k]
        per_video.append(
            {
                "path": str(video_path),
                "predicted": len(predicted),
                "ground_truth": len(ground_truth),
                **counts,
                **prf(counts["tp"], counts["fp"], counts["fn"]),
            }
        )
        print(f"  + {video_path.name}: {counts} {prf(**counts)}")

    report = {
        "iou_threshold": args.iou,
        "videos_evaluated": len(per_video),
        "ensemble": {**totals, **prf(totals["tp"], totals["fp"], totals["fn"])},
        "per_video": per_video,
    }
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nEnsemble: {report['ensemble']}")
    print(f"Saved metrics -> {args.output}")


if __name__ == "__main__":
    main()
