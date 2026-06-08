from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from loguru import logger

from app.scrapers.base import BaseScraper, RawJob
from app.scrapers.decodo_scraper import DecodoScraper, ScraperError
from app.scrapers.playwright_scraper import fetch_html_playwright


class NaukriScraper(BaseScraper):
    def __init__(self, decodo: DecodoScraper):
        self._decodo = decodo

    def _build_url(self, title: str, location: str) -> str:
        slug_title = title.lower().replace(" ", "-")
        slug_loc = location.lower().replace(" ", "-")
        return f"https://www.naukri.com/{slug_title}-jobs-in-{slug_loc}?jobAge=1"

    async def _get_html(self, url: str) -> str:
        try:
            return await self._decodo.fetch_html(url)
        except ScraperError as e:
            logger.warning(f"Decodo failed for Naukri ({e}), falling back to Playwright")
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
                    logger.error(f"Naukri scrape failed for {title}/{location}: {e}")
        return jobs

    def _parse(self, html: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "lxml")
        results = []
        for card in soup.select("article.jobTuple, div.srp-jobtuple-wrapper"):
            title_el = card.select_one("a.title, a.jobTitle")
            company_el = card.select_one("a.subTitle, a.comp-name")
            location_el = card.select_one("li.location span, span.locWdth")
            link_el = card.select_one("a.title[href], a.jobTitle[href]")
            salary_el = card.select_one("li.salary span, span.salary")

            title = title_el.get_text(strip=True) if title_el else ""
            company = company_el.get_text(strip=True) if company_el else "Unknown"
            location = location_el.get_text(strip=True) if location_el else ""
            url = link_el["href"] if link_el else ""
            salary = salary_el.get_text(strip=True) if salary_el else None

            if not title or not url:
                continue

            results.append(RawJob(
                title=title,
                company=company,
                location=location,
                description="",
                url=url,
                source="naukri",
                salary_range=salary,
                is_remote="remote" in location.lower() or "work from home" in location.lower(),
            ))
        return results
