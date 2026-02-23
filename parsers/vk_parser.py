import argparse
from pathlib import Path
import requests


def fetch_vk_posts(token: str, group: str, limit: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    params = {
        "access_token": token,
        "v": "5.199",
        "domain": group,
        "count": limit,
    }
    response = requests.get("https://api.vk.com/method/wall.get", params=params, timeout=30)
    response.raise_for_status()
    items = response.json().get("response", {}).get("items", [])

    for item in items:
        text = item.get("text", "")
        post_id = item.get("id")
        if text:
            (output_dir / f"{post_id}.txt").write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download VK posts for dataset.")
    parser.add_argument("--token", required=True, help="VK API token")
    parser.add_argument("--group", required=True, help="Group short name")
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--output", default="data/raw/vk")
    args = parser.parse_args()

    fetch_vk_posts(args.token, args.group, args.limit, Path(args.output))


if __name__ == "__main__":
    main()
