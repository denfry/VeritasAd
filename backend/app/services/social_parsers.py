import logging
import re
from typing import Dict, Any, Optional
import httpx
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover - optional dependency in some dev containers
    BeautifulSoup = None  # type: ignore[assignment]


def _parse_html(html: str) -> Optional[Any]:
    if BeautifulSoup is None:
        return None
    return BeautifulSoup(html, "html.parser")

async def fetch_telegram_post(url: str) -> Optional[Dict[str, Any]]:
    """Fetch public Telegram post using t.me embed HTML."""
    try:
        # Expected URL format: https://t.me/durov/251
        match = re.search(r't\.me/([^/]+)/(\d+)', url)
        if not match:
            return None
        
        channel = match.group(1)
        post_id = match.group(2)
        embed_url = f"https://t.me/{channel}/{post_id}?embed=1"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(embed_url)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch Telegram embed: {response.status_code}")
                return None
            
            soup = _parse_html(response.text)
            if soup is None:
                return None
            message_box = soup.find('div', class_='tgme_widget_message_text')
            
            if not message_box:
                return None
                
            text = message_box.get_text(separator=' ', strip=True)
            
            author_box = soup.find('div', class_='tgme_widget_message_author_name')
            author = author_box.get_text(strip=True) if author_box else channel
            
            views_box = soup.find('span', class_='tgme_widget_message_views')
            views_text = views_box.get_text(strip=True) if views_box else None
            
            return {
                "id": post_id,
                "title": f"Telegram Post from {author}",
                "description": text,
                "uploader": author,
                "view_count": views_text
            }
    except Exception as e:
        logger.error(f"Error fetching telegram post: {e}")
        return None

async def fetch_vk_post(url: str) -> Optional[Dict[str, Any]]:
    """Fetch VK post using API or basic scraping."""
    # Since we don't have a guaranteed VK API token, attempt basic public scraping
    # or return None to let yt-dlp try its best. We will try a simple public page fetch.
    try:
        # Example format: https://vk.com/wall-123456_789
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            # Need a user agent to avoid basic blocks
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return None
                
            soup = _parse_html(response.text)
            if soup is None:
                return None
            
            # VK post text usually in wall_post_text or pi_text
            text_el = soup.find('div', class_='wall_post_text') or soup.find('div', class_='pi_text')
            if not text_el:
                return None
                
            text = text_el.get_text(separator=' ', strip=True)
            
            # Author
            author_el = soup.find('a', class_='author') or soup.find('a', class_='pi_author')
            author = author_el.get_text(strip=True) if author_el else "Unknown VK Author"
            
            return {
                "id": "vk_post",
                "title": f"VK Post from {author}",
                "description": text,
                "uploader": author,
                "view_count": None
            }
    except Exception as e:
        logger.error(f"Error fetching VK post: {e}")
        return None

async def fetch_instagram_post(url: str) -> Optional[Dict[str, Any]]:
    """Fetch Instagram post metadata using basic scraping."""
    # Instagram is heavily protected. Without a token/cookies, this relies on finding
    # OpenGraph meta tags in the raw response or sharedData.
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return None
            
            soup = _parse_html(response.text)
            if soup is None:
                return None
            
            # Find og:description or title
            og_desc = soup.find('meta', property='og:description')
            og_title = soup.find('meta', property='og:title')
            
            desc_text = og_desc['content'] if og_desc and 'content' in og_desc.attrs else ""
            title_text = og_title['content'] if og_title and 'content' in og_title.attrs else "Instagram Post"
            
            if not desc_text and not title_text:
                return None
                
            return {
                "id": "ig_post",
                "title": title_text,
                "description": desc_text,
                "uploader": "Instagram User",
                "view_count": None
            }
    except Exception as e:
        logger.error(f"Error fetching Instagram post: {e}")
        return None

from urllib.parse import urlparse

async def extract_social_post(url: str) -> Optional[Dict[str, Any]]:
    """Extract metadata for a given URL using custom scrapers."""
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc.lower()
    except Exception:
        return None
    
    if hostname.endswith("t.me") or hostname == "t.me":
        return await fetch_telegram_post(url)
    elif hostname.endswith("vk.com") or hostname == "vk.com" or hostname.endswith("vk.ru") or hostname == "vk.ru":
        return await fetch_vk_post(url)
    elif hostname.endswith("instagram.com") or hostname == "instagram.com" or hostname.endswith("instagr.am") or hostname == "instagr.am":
        return await fetch_instagram_post(url)
        
    return None
