import re
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from app.scrapers.base import RawJob

_BASE = "https://internshala.com"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}

# Map common title terms to Internshala category slugs
_CATEGORY_MAP = {
    "product manager": "product-management",
    "associate product manager": "product-management",
    "product management": "product-management",
    "business analyst": "business-analyst",
    "data analyst": "data-analyst",
    "software engineer": "software-development",
    "frontend": "web-development",
    "backend": "web-development",
    "marketing": "marketing",
    "operations": "operations",
}


def _get_category(title: str) -> str | None:
    tl = title.lower()
    for key, slug in _CATEGORY_MAP.items():
        if key in tl:
            return slug
    return None


class IntershalaScraper:
    """
    Scrapes Internshala jobs (server-side rendered, no login needed).
    Covers freshers/entry-level roles in India.
    """

    def __init__(self, client: httpx.AsyncClient):
        self._c = client

    async def search(self, titles: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []
        urls_to_fetch: list[str] = []

        for title in titles[:4]:
            # Category URL (most reliable)
            cat = _get_category(title)
            if cat:
                urls_to_fetch.append(f"{_BASE}/jobs/{cat}-jobs/")

            # Keyword search URL
            kw = quote_plus(title.lower())
            urls_to_fetch.append(f"{_BASE}/jobs/keyword-{kw}-jobs/")

        # Dedup URLs
        seen_urls: set[str] = set()
        unique_urls = [u for u in urls_to_fetch if not (u in seen_urls or seen_urls.add(u))]

        for url in unique_urls[:5]:
            fetched = await self._fetch_page(url)
            jobs.extend(fetched)

        # Dedup by apply URL
        seen_apply: set[str] = set()
        unique: list[RawJob] = []
        for j in jobs:
            if j.url not in seen_apply:
                seen_apply.add(j.url)
                unique.append(j)

        logger.info(f"Internshala: {len(unique)} jobs")
        return unique

    async def _fetch_page(self, url: str) -> list[RawJob]:
        try:
            r = await self._c.get(url, headers=_HEADERS, timeout=30.0, follow_redirects=True)
            if r.status_code != 200:
                logger.debug(f"Internshala {url}: status {r.status_code}")
                return []
            return self._parse(r.text)
        except Exception as e:
            logger.debug(f"Internshala fetch {url}: {e}")
            return []

    def _parse(self, html: str) -> list[RawJob]:
        soup = BeautifulSoup(html, "lxml")
        jobs: list[RawJob] = []

        for card in soup.select(".individual_internship"):
            try:
                # Title — confirmed selector from HTML inspection
                title_el = card.select_one("#job_title") or card.select_one(".job-title-href")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue

                # URL
                href = title_el.get("href", "") if title_el else ""
                if href and not href.startswith("http"):
                    href = _BASE + href
                if not href:
                    # fallback: data-href on the card itself
                    href = card.get("data-href", "")
                    if href and not href.startswith("http"):
                        href = _BASE + href
                if not href:
                    continue

                # Company
                company_el = card.select_one(".company-name") or card.select_one("p.company-name")
                company = company_el.get_text(strip=True) if company_el else "Unknown"

                # Location — .locations span > a
                loc_parts = [a.get_text(strip=True) for a in card.select(".locations span a")]
                location = ", ".join(loc_parts) if loc_parts else "India"
                if not location:
                    location = "India"

                # Salary — desktop span
                salary_el = card.select_one(".row-1-item .desktop") or card.select_one(".row-1-item span.desktop")
                salary = salary_el.get_text(strip=True) if salary_el else None

                # Description from .about_job .text
                desc_el = card.select_one(".about_job .text")
                description = desc_el.get_text(strip=True)[:2000] if desc_el else f"{title} at {company} — apply on Internshala"

                # Skills
                skills = [s.get_text(strip=True) for s in card.select(".job_skill")]
                if skills:
                    description += f"\n\nSkills required: {', '.join(skills)}"

                jobs.append(RawJob(
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    url=href,
                    source="internshala",
                    salary_range=salary,
                    is_remote="work from home" in location.lower() or "remote" in location.lower(),
                ))
            except Exception as e:
                logger.debug(f"Internshala card parse error: {e}")
                continue

        return jobs
