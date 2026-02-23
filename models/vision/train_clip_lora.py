import argparse
from pathlib import Path
import json


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune CLIP with LoRA adapters.")
    parser.add_argument("--dataset", required=True, help="Path to dataset manifest JSON")
    parser.add_argument("--output", default="models/vision/clip_lora", help="Output directory")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Placeholder: training pipeline should be implemented with transformers + peft.
    # This file provides a consistent entrypoint for future training jobs.
    metadata = {
        "dataset": args.dataset,
        "status": "not_started",
        "notes": "Implement training loop using transformers, peft (LoRA), and evaluate mAP@0.5.",
    }
    (output_dir / "train_state.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
