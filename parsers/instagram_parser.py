import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Instagram data collection placeholder.")
    parser.add_argument("--username", required=True, help="Instagram username")
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--output", default="data/raw/instagram")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    placeholder = output_dir / "README.txt"
    placeholder.write_text(
        "Instagram data collection requires authenticated API access. "
        "Use approved tools or export data manually, then place files here.",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
