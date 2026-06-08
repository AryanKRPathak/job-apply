import httpx
from loguru import logger

from app.config import settings
from app.scrapers.base import RawJob


class ScraperError(Exception):
    pass


class DecodoScraper:
    def __init__(self, http_client: httpx.AsyncClient):
        self._client = http_client

    async def fetch_html(self, url: str) -> str:
        if not settings.decodo_api_key:
            raise ScraperError("Decodo API key not configured")

        response = await self._client.post(
            settings.decodo_api_url,
            headers={"Authorization": f"Bearer {settings.decodo_api_key}"},
            json={"url": url, "render_js": True},
            timeout=60.0,
        )
        if response.status_code != 200:
            raise ScraperError(f"Decodo returned {response.status_code}: {response.text[:200]}")
        data = response.json()
        html = data.get("html") or data.get("content") or ""
        if not html:
            raise ScraperError("Decodo returned empty HTML")
        logger.debug(f"Decodo fetched {len(html)} chars for {url}")
        return html
