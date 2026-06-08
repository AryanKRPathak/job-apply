import asyncio
import re
from urllib.parse import quote_plus

import httpx
from loguru import logger

from app.scrapers.base import RawJob
from app.scrapers.jsearch_scraper import JSearchScraper
from app.scrapers.internshala_scraper import IntershalaScraper

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobSearchBot/1.0)"}

# Greenhouse slugs for Indian + global tech companies with PM hiring
_GREENHOUSE_COMPANIES = [
    "postman", "druva", "freshworks", "browserstack", "chargebee",
    "setu-api", "razorpay", "sprinklr", "moengage", "clevertap",
    "leadsquared", "darwinbox", "mindtickle", "uniphore", "icertis",
    "exotel", "kaleyra", "netcore", "hasura", "capillarytech",
    "stripe", "notion", "figma", "linear", "vercel",
    "airtable", "rippling", "gusto", "brex", "ramp",
    "plaid", "lattice", "greenhouse", "lever", "workday",
]

# Lever slugs for Indian + global companies
_LEVER_COMPANIES = [
    "cred", "swiggy", "ola", "oyo", "udaan", "navi",
    "slice-2", "groww", "zepto", "pristyncare", "practo",
    "cars24", "spinny", "zestmoney", "moneyview", "healthifyme",
    "locus", "ninjacart", "zetwerk", "ofbusiness", "innoscripta",
    "coinbase", "databricks", "grafana-labs", "mixpanel", "amplitude",
    "segment", "heap", "fullstory", "pendo", "productboard",
]


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").strip()


_STOPWORDS = {"and", "the", "for", "with", "from", "into", "that", "this", "are", "was"}

# Common abbreviations / aliases — if job title contains these, treat as a match
_PM_ALIASES = {"apm", " pm ", "( pm)", "head of product", "vp product", "vp of product",
               "director of product", "chief product", "cpo"}


def _is_pm_title(job_title: str, target_titles: list[str]) -> bool:
    """
    Return True only when the job title is a genuine match for the user's targets.

    Rules (any one is sufficient):
    1. The full target phrase appears as a substring in the job title.
    2. ALL significant words (len > 3, not stopwords) from the target appear in the title.
    3. Known PM aliases match.
    """
    jt = job_title.lower()

    # Rule 3: alias match
    if any(alias in jt for alias in _PM_ALIASES):
        return True

    for target in target_titles:
        tl = target.lower()

        # Rule 1: exact phrase match (e.g. "product manager" in "Senior Product Manager")
        if tl in jt:
            return True

        # Rule 2: ALL significant words must appear
        sig_words = [w for w in tl.split() if len(w) > 3 and w not in _STOPWORDS]
        if sig_words and all(w in jt for w in sig_words):
            return True

    return False


class FreeJobScraper:
    """
    Multi-source free job scraper with PM-aware title filtering.
    Sources:
      • Remotive      — remote tech jobs, search by keyword
      • RemoteOK      — remote jobs, product-manager tagged
      • Arbeitnow     — international board, 100 results/query
      • Jobicy        — remote-first board
      • Greenhouse    — 30+ Indian & global tech company career pages
      • Lever         — 30+ Indian & global tech company career pages
    """

    def __init__(self, client: httpx.AsyncClient):
        self._c = client

    async def scrape_all(self, titles: list[str], locations: list[str]) -> list[RawJob]:
        jsearch = JSearchScraper(self._c)
        internshala = IntershalaScraper(self._c)

        # Build JSearch queries: "product manager in Bangalore", "product manager in Remote India"
        jsearch_queries = []
        for title in titles[:3]:
            for loc in locations[:3]:
                jsearch_queries.append(f"{title} in {loc}")
            jsearch_queries.append(f"{title} in India")  # broad India search always

        tasks = [
            self._remotive(titles),
            self._remoteok(titles),
            self._arbeitnow(titles),
            self._jobicy(titles),
            self._greenhouse(titles),
            self._lever(titles),
            internshala.search(titles),
            *[jsearch.search(q, pages=2) for q in jsearch_queries[:8]],
        ]

        batches = await asyncio.gather(*tasks, return_exceptions=True)

        jobs: list[RawJob] = []
        for b in batches:
            if isinstance(b, Exception):
                logger.warning(f"Scraper batch error: {b}")
            else:
                jobs.extend(b)

        # URL-level dedup
        seen: set[str] = set()
        unique: list[RawJob] = []
        for j in jobs:
            key = j.url.strip()
            if key and key not in seen:
                seen.add(key)
                unique.append(j)

        logger.info(f"FreeJobScraper: {len(unique)} unique jobs after dedup")
        return unique

    # ------------------------------------------------------------------ #
    # Remotive
    # ------------------------------------------------------------------ #
    async def _remotive(self, titles: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []
        for title in titles[:5]:
            try:
                r = await self._c.get(
                    "https://remotive.com/api/remote-jobs",
                    params={"search": title, "limit": 50},
                    timeout=30.0,
                    headers=_HEADERS,
                )
                r.raise_for_status()
                for j in r.json().get("jobs", []):
                    if not j.get("url"):
                        continue
                    if not _is_pm_title(j.get("title", ""), titles):
                        continue
                    jobs.append(RawJob(
                        title=j.get("title", ""),
                        company=j.get("company_name", "Unknown"),
                        location=j.get("candidate_required_location", "Remote"),
                        description=_strip_html(j.get("description", ""))[:4000],
                        url=j.get("url", ""),
                        source="remotive",
                        salary_range=j.get("salary") or None,
                        is_remote=True,
                    ))
            except Exception as e:
                logger.error(f"Remotive failed ({title}): {e}")
        logger.info(f"Remotive: {len(jobs)} PM-relevant jobs")
        return jobs

    # ------------------------------------------------------------------ #
    # RemoteOK
    # ------------------------------------------------------------------ #
    async def _remoteok(self, titles: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []
        try:
            r = await self._c.get(
                "https://remoteok.com/api?tag=product-manager",
                timeout=30.0,
                headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
            )
            r.raise_for_status()
            for j in r.json():
                if not isinstance(j, dict) or not j.get("url"):
                    continue
                jt = j.get("position", "")
                if not _is_pm_title(jt, titles):
                    continue
                jobs.append(RawJob(
                    title=jt,
                    company=j.get("company", "Unknown"),
                    location=j.get("location", "Remote") or "Remote",
                    description=_strip_html(j.get("description", ""))[:4000],
                    url=j.get("url", ""),
                    source="remoteok",
                    salary_range=(
                        f"${j['salary_min']}–${j['salary_max']}"
                        if j.get("salary_min") and j.get("salary_max") else None
                    ),
                    is_remote=True,
                ))
        except Exception as e:
            logger.error(f"RemoteOK failed: {e}")
        logger.info(f"RemoteOK: {len(jobs)} PM-relevant jobs")
        return jobs

    # ------------------------------------------------------------------ #
    # Arbeitnow
    # ------------------------------------------------------------------ #
    async def _arbeitnow(self, titles: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []
        for title in titles[:5]:
            try:
                r = await self._c.get(
                    "https://www.arbeitnow.com/api/job-board-api",
                    params={"search": title},
                    timeout=30.0,
                    headers=_HEADERS,
                )
                r.raise_for_status()
                for j in r.json().get("data", []):
                    if not j.get("url"):
                        continue
                    if not _is_pm_title(j.get("title", ""), titles):
                        continue
                    jobs.append(RawJob(
                        title=j.get("title", ""),
                        company=j.get("company_name", "Unknown"),
                        location=j.get("location", ""),
                        description=_strip_html(j.get("description", ""))[:4000],
                        url=j.get("url", ""),
                        source="arbeitnow",
                        is_remote=bool(j.get("remote")),
                    ))
            except Exception as e:
                logger.error(f"Arbeitnow failed ({title}): {e}")
        logger.info(f"Arbeitnow: {len(jobs)} PM-relevant jobs")
        return jobs

    # ------------------------------------------------------------------ #
    # Jobicy
    # ------------------------------------------------------------------ #
    async def _jobicy(self, titles: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []
        for title in titles[:5]:
            try:
                r = await self._c.get(
                    "https://jobicy.com/api/v2/remote-jobs",
                    params={"tag": title, "count": 50},
                    timeout=30.0,
                    headers=_HEADERS,
                )
                r.raise_for_status()
                for j in r.json().get("jobs", []):
                    jt = j.get("jobTitle", "")
                    url = j.get("url", "")
                    if not url or not _is_pm_title(jt, titles):
                        continue
                    salary = None
                    if j.get("annualSalaryMin"):
                        salary = f"${j['annualSalaryMin']}–${j.get('annualSalaryMax', '?')}"
                    jobs.append(RawJob(
                        title=jt,
                        company=j.get("companyName", "Unknown"),
                        location=j.get("jobGeo", "Remote"),
                        description=_strip_html(j.get("jobExcerpt", ""))[:4000],
                        url=url if url.startswith("http") else f"https://jobicy.com{url}",
                        source="jobicy",
                        salary_range=salary,
                        is_remote=True,
                    ))
            except Exception as e:
                logger.error(f"Jobicy failed ({title}): {e}")
        logger.info(f"Jobicy: {len(jobs)} PM-relevant jobs")
        return jobs

    # ------------------------------------------------------------------ #
    # Greenhouse  (public job boards — no auth needed)
    # ------------------------------------------------------------------ #
    async def _greenhouse(self, titles: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []

        async def fetch_company(slug: str):
            try:
                r = await self._c.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
                    timeout=15.0,
                    headers=_HEADERS,
                )
                if r.status_code != 200:
                    return
                for j in r.json().get("jobs", []):
                    jt = j.get("title", "")
                    url = j.get("absolute_url", "")
                    if not url or not _is_pm_title(jt, titles):
                        continue
                    location = ""
                    offices = j.get("offices") or j.get("location") or []
                    if isinstance(offices, list) and offices:
                        location = offices[0].get("name", "")
                    elif isinstance(offices, dict):
                        location = offices.get("name", "")
                    jobs.append(RawJob(
                        title=jt,
                        company=slug.replace("-", " ").title(),
                        location=location,
                        description="",
                        url=url,
                        source="greenhouse",
                        is_remote="remote" in (location or jt).lower(),
                    ))
            except Exception as e:
                logger.debug(f"Greenhouse {slug}: {e}")

        await asyncio.gather(*[fetch_company(s) for s in _GREENHOUSE_COMPANIES])
        logger.info(f"Greenhouse: {len(jobs)} PM-relevant jobs")
        return jobs

    # ------------------------------------------------------------------ #
    # Lever  (public job boards — no auth needed)
    # ------------------------------------------------------------------ #
    async def _lever(self, titles: list[str]) -> list[RawJob]:
        jobs: list[RawJob] = []

        async def fetch_company(slug: str):
            try:
                r = await self._c.get(
                    f"https://api.lever.co/v0/postings/{slug}?mode=json",
                    timeout=15.0,
                    headers=_HEADERS,
                )
                if r.status_code != 200:
                    return
                for j in r.json():
                    jt = j.get("text", "")
                    url = j.get("hostedUrl", "")
                    if not url or not _is_pm_title(jt, titles):
                        continue
                    location = j.get("categories", {}).get("location", "") or j.get("workplaceType", "")
                    jobs.append(RawJob(
                        title=jt,
                        company=slug.replace("-", " ").title(),
                        location=location,
                        description=_strip_html(j.get("descriptionPlain", "") or j.get("description", ""))[:4000],
                        url=url,
                        source="lever",
                        is_remote="remote" in (location or jt).lower(),
                    ))
            except Exception as e:
                logger.debug(f"Lever {slug}: {e}")

        await asyncio.gather(*[fetch_company(s) for s in _LEVER_COMPANIES])
        logger.info(f"Lever: {len(jobs)} PM-relevant jobs")
        return jobs
