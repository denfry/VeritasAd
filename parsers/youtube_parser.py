import argparse
from pathlib import Path
import subprocess


def download_channel(channel_url: str, limit: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "yt-dlp",
        "--playlist-items",
        f"1-{limit}",
        "-o",
        str(output_dir / "%(uploader)s_%(id)s.%(ext)s"),
        channel_url,
    ]
    subprocess.run(cmd, check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download YouTube videos for dataset.")
    parser.add_argument("--channel", required=True, help="Channel URL")
    parser.add_argument("--limit", type=int, default=200, help="Number of videos")
    parser.add_argument("--output", default="data/raw/youtube", help="Output directory")
    args = parser.parse_args()

    download_channel(args.channel, args.limit, Path(args.output))


if __name__ == "__main__":
    main()
