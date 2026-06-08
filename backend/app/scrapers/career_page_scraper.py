import re
from urllib.parse import urlparse

import httpx
from loguru import logger

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
CONTACT_PATH_HINTS = ["/about", "/team", "/contact", "/careers/team", "/people"]
SKIP_DOMAINS = ["example.com", "sentry", "noreply", "no-reply", "wix.com", "schema.org"]


async def scrape_career_contacts(job_url: str, company: str) -> list[dict]:
    parsed = urlparse(job_url)
    base = f"{parsed.scheme}://{parsed.netloc}"

    contacts = []
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        for path in CONTACT_PATH_HINTS:
            url = base + path
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code != 200:
                    continue
                emails = EMAIL_RE.findall(resp.text)
                for email in set(emails):
                    if any(skip in email for skip in SKIP_DOMAINS):
                        continue
                    contacts.append({
                        "email": email,
                        "name": None,
                        "title": None,
                        "linkedin_url": None,
                        "source": "website",
                    })
                if contacts:
                    break
            except Exception as e:
                logger.debug(f"Career page scrape failed for {url}: {e}")

    return contacts
