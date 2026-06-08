from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from loguru import logger

from app.scrapers.base import BaseScraper, RawJob
from app.scrapers.decodo_scraper import DecodoScraper, ScraperError
from app.scrapers.playwright_scraper import fetch_html_playwright


class LinkedInScraper(BaseScraper):
    def __init__(self, decodo: DecodoScraper):
        self._decodo = decodo

    def _build_url(self, title: str, location: str) -> str:
        return (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={quote_plus(title)}&location={quote_plus(location)}&f_TPR=r86400&position=1&pageNum=0"
        )

    async def _get_html(self, url: str) -> str:
        try:
            return await self._decodo.fetch_html(url)
        except ScraperError as e:
            logger.warning(f"Decodo failed for LinkedIn ({e}), falling back to Playwright")
            return await fetch_html_playwright(url)

    async def fetch_jobs(self, titles: list[str], locations: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []
        for title in titles:
            for location in locations:
                url = self._build_url(title, location)
                try:
                    html = await self._get_html(url)
                    jobs.extend(self._parse(html))
                except Exception as e:
                    logger.error(f"LinkedIn scrape failed for {title}/{location}: {e}")
        return jobs

    def _parse(self, html: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "lxml")
        results = []
        for card in soup.select("li.jobs-search__results-list > li, div.base-card"):
            title_el = card.select_one("h3.base-search-card__title, h3.job-search-card__title")
            company_el = card.select_one("h4.base-search-card__subtitle, a.job-search-card__company-name")
            location_el = card.select_one("span.job-search-card__location")
            link_el = card.select_one("a.base-card__full-link, a[data-tracking-control-name='public_jobs_jserp-result_search-card']")

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            location = location_el.get_text(strip=True) if location_el else ""
            url = link_el["href"].split("?")[0] if link_el else ""

            if not title or not url:
                continue

            results.append(RawJob(
                title=title,
                company=company,
                location=location,
                description="",
                url=url,
                source="linkedin",
                is_remote="remote" in location.lower(),
            ))
        return results
