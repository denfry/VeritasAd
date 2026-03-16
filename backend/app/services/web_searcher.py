import httpx
import logging
import re
from html import unescape
from typing import List, Dict

logger = logging.getLogger(__name__)


class WebSearcher:
    """Utility to perform web searches using DuckDuckGo HTML Lite."""

    _tr_re = re.compile(r"<tr[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
    _snippet_re = re.compile(
        r'<td[^>]*class=["\']result-snippet["\'][^>]*>(.*?)</td>',
        re.IGNORECASE | re.DOTALL,
    )
    _title_re = re.compile(
        r'<a[^>]*class=["\']result-url["\'][^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    _tag_re = re.compile(r"<[^>]+>")

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def search_async(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Perform an async search."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                url = "https://lite.duckduckgo.com/lite/"
                data = {"q": query}
                response = await client.post(url, data=data)
                response.raise_for_status()
                return self._parse_html(response.text, max_results)
        except Exception as e:
            logger.error(f"Async Web search failed for query '{query}': {e}")
            return []

    def search_sync(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Perform a sync search."""
        try:
            with httpx.Client(timeout=self.timeout, headers=self.headers) as client:
                url = "https://lite.duckduckgo.com/lite/"
                data = {"q": query}
                response = client.post(url, data=data)
                response.raise_for_status()
                return self._parse_html(response.text, max_results)
        except Exception as e:
            logger.error(f"Sync Web search failed for query '{query}': {e}")
            return []

    def _parse_html(self, html: str, max_results: int) -> List[Dict[str, str]]:
        rows = self._tr_re.finditer(html)
        results: List[Dict[str, str]] = []
        prev_row_html = ""

        for row_match in rows:
            row_html = row_match.group(1)
            snippet_match = self._snippet_re.search(row_html)
            if snippet_match:
                title = ""
                title_match = self._title_re.search(prev_row_html)
                if title_match:
                    title = self._strip_html(title_match.group(1))

                snippet = self._strip_html(snippet_match.group(1))
                if snippet:
                    results.append({"title": title, "snippet": snippet})
                if len(results) >= max_results:
                    break

            prev_row_html = row_html

        return results

    def _strip_html(self, fragment: str) -> str:
        text = self._tag_re.sub(" ", fragment)
        return unescape(text).strip()
