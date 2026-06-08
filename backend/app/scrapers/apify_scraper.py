import httpx
from loguru import logger

from app.config import settings
from app.scrapers.base import RawJob


class ApifyScraper:
    """Single scraper that calls Apify cloud actors — no browser on your machine."""

    BASE_URL = "https://api.apify.com/v2"

    def __init__(self, http_client: httpx.AsyncClient):
        self._client = http_client
        self._headers = {"Authorization": f"Bearer {settings.apify_token}"}

    async def _run_actor(self, actor_id: str, input_data: dict) -> list[dict]:
        """Start an actor, wait for it to finish, return dataset items."""
        # Start the run
        start_resp = await self._client.post(
            f"{self.BASE_URL}/acts/{actor_id}/runs",
            headers=self._headers,
            json=input_data,
            timeout=10.0,
        )
        start_resp.raise_for_status()
        run = start_resp.json()["data"]
        run_id = run["id"]
        logger.info(f"Apify actor {actor_id} started — run {run_id}")

        # Poll until done (max 5 minutes)
        import asyncio
        for _ in range(60):
            await asyncio.sleep(5)
            status_resp = await self._client.get(
                f"{self.BASE_URL}/actor-runs/{run_id}",
                headers=self._headers,
                timeout=10.0,
            )
            status_resp.raise_for_status()
            status = status_resp.json()["data"]["status"]
            if status == "SUCCEEDED":
                break
            if status in ("FAILED", "ABORTED", "TIMED-OUT"):
                raise RuntimeError(f"Apify run {run_id} ended with status: {status}")

        # Fetch dataset items
        dataset_id = status_resp.json()["data"]["defaultDatasetId"]
        items_resp = await self._client.get(
            f"{self.BASE_URL}/datasets/{dataset_id}/items",
            headers=self._headers,
            params={"format": "json", "clean": "true"},
            timeout=30.0,
        )
        items_resp.raise_for_status()
        return items_resp.json()

    async def scrape_linkedin_jobs(self, titles: list[str], locations: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []
        for title in titles:
            for location in locations:
                try:
                    items = await self._run_actor(
                        "harvestapi/linkedin-job-search",
                        {
                            "keyword": title,
                            "location": location,
                            "datePosted": "past24Hours",
                            "limit": 25,
                        },
                    )
                    for item in items:
                        jobs.append(RawJob(
                            title=item.get("title", ""),
                            company=item.get("company", "Unknown"),
                            location=item.get("location", ""),
                            description=item.get("description", ""),
                            url=item.get("jobUrl", ""),
                            source="linkedin",
                            is_remote="remote" in (item.get("location") or "").lower(),
                        ))
                    logger.info(f"LinkedIn: {len(items)} jobs for '{title}' in '{location}'")
                except Exception as e:
                    logger.error(f"LinkedIn Apify scrape failed for {title}/{location}: {e}")
        return jobs

    @staticmethod
    def _country_code(location: str) -> str:
        india_hints = {"india", "bangalore", "bengaluru", "mumbai", "delhi", "hyderabad",
                       "pune", "chennai", "kolkata", "noida", "gurugram", "gurgaon", "remote"}
        loc_lower = location.lower()
        if any(hint in loc_lower for hint in india_hints):
            return "IN"
        return "US"

    async def scrape_indeed_jobs(self, titles: list[str], locations: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []
        for title in titles:
            for location in locations:
                try:
                    items = await self._run_actor(
                        "misceres/indeed-scraper",
                        {
                            "position": title,
                            "country": self._country_code(location),
                            "location": location,
                            "maxItems": 25,
                        },
                    )
                    for item in items:
                        jobs.append(RawJob(
                            title=item.get("positionName", title),
                            company=item.get("company", "Unknown"),
                            location=item.get("location", location),
                            description=item.get("description", ""),
                            url=item.get("url", ""),
                            source="indeed",
                            salary_range=item.get("salary"),
                            is_remote="remote" in (item.get("location") or "").lower(),
                        ))
                    logger.info(f"Indeed: {len(items)} jobs for '{title}' in '{location}'")
                except Exception as e:
                    logger.error(f"Indeed Apify scrape failed for {title}/{location}: {e}")
        return jobs

    async def scrape_naukri_jobs(self, titles: list[str], locations: list[str]) -> list[RawJob]:
        """Naukri via Apify generic web scraper."""
        from urllib.parse import quote_plus
        jobs: list[RawJob] = []
        for title in titles:
            for location in locations:
                url = f"https://www.naukri.com/{quote_plus(title.lower().replace(' ', '-'))}-jobs-in-{quote_plus(location.lower().replace(' ', '-'))}"
                try:
                    items = await self._run_actor(
                        "apify/cheerio-scraper",
                        {
                            "startUrls": [{"url": url}],
                            "maxCrawlingDepth": 0,
                            "maxPagesPerCrawl": 1,
                        },
                    )
                    # Parse raw HTML from cheerio result
                    for item in items:
                        if item.get("title") and item.get("url"):
                            jobs.append(RawJob(
                                title=item.get("title", ""),
                                company=item.get("company", "Unknown"),
                                location=location,
                                description=item.get("description", ""),
                                url=item.get("url", ""),
                                source="naukri",
                            ))
                    logger.info(f"Naukri: {len(jobs)} jobs for '{title}' in '{location}'")
                except Exception as e:
                    logger.error(f"Naukri Apify scrape failed for {title}/{location}: {e}")
        return jobs
