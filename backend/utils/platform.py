import re
from typing import Literal

Platform = Literal["telegram", "vk", "youtube", "rutube", "twitch", "other"]


def detect_platform(url: str) -> Platform:
    url_low = url.lower()
    if "t.me" in url_low or "telegram.me" in url_low:
        return "telegram"
    if "vk.com" in url_low or "vkontakte.ru" in url_low:
        return "vk"
    if "youtube.com" in url_low or "youtu.be" in url_low:
        return "youtube"
    if "rutube.ru" in url_low:
        return "rutube"
    if "twitch.tv" in url_low:
        return "twitch"
    return "other"


def parse_telegram_url(url: str) -> tuple[str, int]:
    match = re.match(r"https?://t\.me/(\w+)/(\d+)", url)
    if not match:
        raise ValueError("Неподдерживаемый формат Telegram URL")
    return match.group(1), int(match.group(2))

