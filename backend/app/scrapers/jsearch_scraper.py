import httpx
from loguru import logger

from app.config import settings
from app.scrapers.base import RawJob

_HOST = "jsearch.p.rapidapi.com"
_BASE = f"https://{_HOST}/search"


class JSearchScraper:
    """
    JSearch on RapidAPI — queries Google Jobs which aggregates LinkedIn,
    Indeed, Naukri, Glassdoor, and hundreds of other boards.
    Free tier: 500 requests/month.
    Sign up: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
    """

    def __init__(self, client: httpx.AsyncClient):
        self._c = client
        self._headers = {
            "X-RapidAPI-Key": settings.jsearch_api_key,
            "X-RapidAPI-Host": _HOST,
        }

    async def search(self, query: str, pages: int = 2) -> list[RawJob]:
        if not settings.jsearch_api_key:
            logger.warning("JSearch: no API key set — skipping")
            return []

        jobs: list[RawJob] = []
        for page in range(1, pages + 1):
            try:
                r = await self._c.get(
                    _BASE,
                    headers=self._headers,
                    params={
                        "query": query,
                        "page": str(page),
                        "num_pages": "1",
                        "date_posted": "month",
                    },
                    timeout=30.0,
                )
                r.raise_for_status()
                for j in r.json().get("data", []):
                    url = j.get("job_apply_link", "") or j.get("job_google_link", "")
                    if not url:
                        continue

                    salary = None
                    if j.get("job_min_salary") and j.get("job_max_salary"):
                        curr = j.get("job_salary_currency", "$")
                        salary = f"{curr}{int(j['job_min_salary'])}–{curr}{int(j['job_max_salary'])}"

                    location_parts = [
                        p for p in [j.get("job_city"), j.get("job_state"), j.get("job_country")]
                        if p
                    ]
                    location = ", ".join(location_parts)

                    source = (j.get("job_publisher") or "jsearch").lower().replace(" ", "")
                    # Normalize common publishers
                    if "linkedin" in source:
                        source = "linkedin"
                    elif "indeed" in source:
                        source = "indeed"
                    elif "naukri" in source:
                        source = "naukri"
                    elif "glassdoor" in source:
                        source = "glassdoor"
                    else:
                        source = "jsearch"

                    jobs.append(RawJob(
                        title=j.get("job_title", ""),
                        company=j.get("employer_name", "Unknown"),
                        location=location,
                        description=(j.get("job_description") or "")[:4000],
                        url=url,
                        source=source,
                        salary_range=salary,
                        is_remote=bool(j.get("job_is_remote")),
                    ))
            except Exception as e:
                logger.error(f"JSearch failed (query='{query}', page={page}): {e}")
                break

        logger.info(f"JSearch '{query}': {len(jobs)} jobs")
        return jobs
