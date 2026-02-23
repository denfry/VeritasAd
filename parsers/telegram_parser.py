import argparse
from pathlib import Path
from telethon import TelegramClient


async def download_messages(api_id: int, api_hash: str, channel: str, limit: int, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    async with TelegramClient("veritasad_session", api_id, api_hash) as client:
        async for message in client.iter_messages(channel, limit=limit):
            if not message.text:
                continue
            file_path = output_dir / f"{message.id}.txt"
            file_path.write_text(message.text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download Telegram posts for dataset.")
    parser.add_argument("--api-id", type=int, required=True)
    parser.add_argument("--api-hash", required=True)
    parser.add_argument("--channel", required=True, help="@channel_name")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--output", default="data/raw/telegram")
    args = parser.parse_args()

    import asyncio

    asyncio.run(
        download_messages(args.api_id, args.api_hash, args.channel, args.limit, Path(args.output))
    )


if __name__ == "__main__":
    main()
