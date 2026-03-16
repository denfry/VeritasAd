import httpx
from bs4 import BeautifulSoup
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class WebSearcher:
    """Utility to perform web searches using DuckDuckGo HTML Lite."""

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
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for tr in soup.find_all('tr'):
            td = tr.find('td', class_='result-snippet')
            if td:
                snippet = td.get_text(strip=True)
                # Find the previous tr for the title
                prev_tr = tr.find_previous_sibling('tr')
                title = ""
                if prev_tr:
                    title_a = prev_tr.find('a', class_='result-url')
                    if title_a:
                        title = title_a.get_text(strip=True)
                
                if snippet:
                    results.append({
                        "title": title,
                        "snippet": snippet
                    })
                
                if len(results) >= max_results:
                    break
                    
        return results
