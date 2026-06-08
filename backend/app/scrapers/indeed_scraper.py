from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from loguru import logger

from app.scrapers.base import BaseScraper, RawJob
from app.scrapers.decodo_scraper import DecodoScraper, ScraperError
from app.scrapers.playwright_scraper import fetch_html_playwright


class IndeedScraper(BaseScraper):
    def __init__(self, decodo: DecodoScraper):
        self._decodo = decodo

    def _build_url(self, title: str, location: str) -> str:
        return f"https://www.indeed.com/jobs?q={quote_plus(title)}&l={quote_plus(location)}&fromage=1"

    async def _get_html(self, url: str) -> str:
        try:
            return await self._decodo.fetch_html(url)
        except ScraperError as e:
            logger.warning(f"Decodo failed for Indeed ({e}), falling back to Playwright")
            return await fetch_html_playwright(url)

    async def fetch_jobs(self, titles: list[str], locations: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []
        for title in titles:
            for location in locations:
                url = self._build_url(title, location)
                try:
                    html = await self._get_html(url)
                    jobs.extend(self._parse(html, title))
                except Exception as e:
                    logger.error(f"Indeed scrape failed for {title}/{location}: {e}")
        return jobs

    def _parse(self, html: str, fallback_title: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "lxml")
        results = []
        for card in soup.select("div.job_seen_beacon, div[data-jk]"):
            title_el = card.select_one("h2.jobTitle span, h2 a span")
            company_el = card.select_one("span[data-testid='company-name'], .companyName")
            location_el = card.select_one("div[data-testid='text-location'], .companyLocation")
            link_el = card.select_one("h2 a[href]")
            salary_el = card.select_one("div[data-testid='attribute_snippet_testid']")

            title = title_el.get_text(strip=True) if title_el else fallback_title
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            location = location_el.get_text(strip=True) if location_el else ""
            href = link_el["href"] if link_el else ""
            url = f"https://www.indeed.com{href}" if href.startswith("/") else href
            salary = salary_el.get_text(strip=True) if salary_el else None

            if not url:
                continue

            results.append(RawJob(
                title=title,
                company=company,
                location=location,
                description="",
                url=url,
                source="indeed",
                salary_range=salary,
                is_remote="remote" in location.lower(),
            ))
        return results
