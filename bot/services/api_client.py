import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class VeritasAdApiClient:
    """API client for VeritasAd backend."""

    def __init__(self, base_url: str, timeout: float = 90.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        logger.info(f"API Client initialized with base_url={self.base_url}, timeout={self.timeout}s")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            )
            logger.debug(f"Created new HTTP client for {self.base_url}")
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.debug("HTTP client closed")

    async def analyze_url(self, api_key: str, url: str) -> dict:
        """Analyze video by URL."""
        logger.info(f"Analyzing URL: {url}")
        client = await self._get_client()
        try:
            logger.debug(f"Sending POST request to {self.base_url}/api/v1/analyze/check")
            response = await client.post(
                f"{self.base_url}/api/v1/analyze/check",
                data={"url": url},
                headers={"X-API-Key": api_key},
            )
            logger.debug(f"Response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            logger.info(f"Analysis started, task_id={result.get('task_id', 'N/A')}")
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error analyzing URL: {e.response.status_code} - {e.response.text[:200] if e.response.text else 'No details'}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error analyzing URL: {type(e).__name__} - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error analyzing URL: {type(e).__name__} - {str(e)}")
            raise

    async def analyze_file(self, api_key: str, filename: str, content: bytes) -> dict:
        """Analyze video file."""
        logger.info(f"Analyzing file: {filename} ({len(content)} bytes)")
        client = await self._get_client()
        try:
            files = {"file": (filename, content, "video/mp4")}
            logger.debug(f"Sending POST request to {self.base_url}/api/v1/analyze/check with file")
            response = await client.post(
                f"{self.base_url}/api/v1/analyze/check",
                files=files,
                headers={"X-API-Key": api_key},
            )
            logger.debug(f"Response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            logger.info(f"Analysis started, task_id={result.get('task_id', 'N/A')}")
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error analyzing file: {e.response.status_code} - {e.response.text[:200] if e.response.text else 'No details'}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error analyzing file: {type(e).__name__} - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error analyzing file: {type(e).__name__} - {str(e)}")
            raise

    async def health_check(self, api_key: str) -> Optional[dict]:
        """Check backend health."""
        client = await self._get_client()
        try:
            logger.debug(f"Checking backend health at {self.base_url}/health")
            response = await client.get(
                f"{self.base_url}/health",
                headers={"X-API-Key": api_key},
                timeout=15.0,
            )
            if response.status_code != 200:
                logger.warning(f"Health check returned status {response.status_code}")
                return None
            logger.info("Backend health check passed")
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Health check failed: {type(e).__name__} - {str(e)}")
            return None

    async def get_task_status(self, api_key: str, task_id: str) -> dict:
        """Get task progress status."""
        logger.debug(f"Getting task status for task_id={task_id}")
        client = await self._get_client()
        try:
            response = await client.get(
                f"{self.base_url}/api/v1/progress/analysis/{task_id}/status",
                headers={"X-API-Key": api_key},
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Task {task_id} status: {result.get('status', 'unknown')} - {result.get('progress', 0)}%")
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting task status: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error getting task status: {type(e).__name__} - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting task status: {type(e).__name__} - {str(e)}")
            raise

    async def get_task_result(self, api_key: str, task_id: str) -> dict:
        """Get final task result."""
        logger.info(f"Getting task result for task_id={task_id}")
        client = await self._get_client()
        try:
            response = await client.get(
                f"{self.base_url}/api/v1/progress/analysis/{task_id}/result",
                headers={"X-API-Key": api_key},
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Task {task_id} result: status={result.get('status', 'unknown')}")
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting task result: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error getting task result: {type(e).__name__} - {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting task result: {type(e).__name__} - {str(e)}")
            raise
