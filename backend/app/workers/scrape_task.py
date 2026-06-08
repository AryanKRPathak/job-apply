import asyncio
import uuid
from datetime import datetime, timezone

import httpx
from loguru import logger
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.job import Job
from app.models.profile import CandidateProfile
from app.scrapers.free_job_scraper import FreeJobScraper
from app.services.cover_letter import generate_cover_letter
from app.services.deduplicator import compute_external_id
from app.services.job_scorer import score_job


def _passes_filters(raw, profile: CandidateProfile) -> tuple[bool, str]:
    """Return (passes, reason). Runs before any AI calls to save tokens."""
    company_lower = raw.company.lower()
    title_lower = raw.title.lower()

    # Feature 1 — company whitelist (if set, only allow listed companies)
    if profile.company_whitelist:
        wl = [c.lower() for c in profile.company_whitelist]
        if not any(w in company_lower for w in wl):
            return False, f"company '{raw.company}' not in whitelist"

    # Feature 1 — company blacklist
    if profile.company_blacklist:
        bl = [c.lower() for c in profile.company_blacklist]
        if any(b in company_lower for b in bl):
            return False, f"company '{raw.company}' is blacklisted"

    # Feature 3 — title keyword blacklist
    if profile.title_keyword_blacklist:
        kbl = [k.lower() for k in profile.title_keyword_blacklist]
        for kw in kbl:
            if kw in title_lower:
                return False, f"title contains blacklisted keyword '{kw}'"

    # Feature 4 — salary floor (only applies when the job advertises a salary)
    if profile.min_salary and raw.salary_range:
        # Extract first number found in salary string (e.g. "₹8-12 LPA" → 8, "$80k" → 80)
        import re
        nums = re.findall(r"\d[\d,]*", raw.salary_range.replace(",", ""))
        if nums:
            first_num = int(nums[0])
            # Heuristic: if number looks like a monthly figure (< 1000), convert to annual
            annual = first_num * 12 if first_num < 1000 else first_num
            if annual < profile.min_salary:
                return False, f"salary {raw.salary_range} below floor {profile.min_salary}"

    return True, ""


async def run_scrape_pipeline(profile_id: str, portals: list[str]) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(CandidateProfile).where(CandidateProfile.id == uuid.UUID(profile_id))
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise ValueError(f"Profile {profile_id} not found")

        titles = profile.target_titles or []
        locations = profile.target_locations or []

        if not titles:
            raise ValueError("Add at least one target job title in your profile before scraping.")
        if not locations:
            raise ValueError("Add at least one target location in your profile before scraping.")

        profile_dict = {
            "full_name": profile.full_name,
            "target_titles": titles,
            "target_locations": locations,
            "skills": profile.skills or [],
            "years_exp": profile.years_exp,
            "story": profile.story or "",
        }

        async with httpx.AsyncClient(timeout=60.0) as http_client:
            scraper = FreeJobScraper(http_client)
            raw_jobs = await scraper.scrape_all(titles, locations)

        logger.info(f"Scraper returned {len(raw_jobs)} raw jobs")

        total_found = len(raw_jobs)
        total_new = 0
        filtered_out = 0

        for raw in raw_jobs:
            if not raw.url:
                continue

            # Apply pre-AI filters
            passes, reason = _passes_filters(raw, profile)
            if not passes:
                logger.debug(f"Filtered out '{raw.title}' @ {raw.company}: {reason}")
                filtered_out += 1
                continue

            ext_id = compute_external_id(raw.title, raw.company, raw.url)
            exists = await db.execute(select(Job).where(Job.external_id == ext_id))
            if exists.scalar_one_or_none():
                continue

            try:
                score_result = await score_job(profile_dict, {
                    "title": raw.title,
                    "company": raw.company,
                    "location": raw.location,
                    "description": raw.description,
                })
            except Exception as e:
                logger.warning(f"Scoring failed for '{raw.title}': {e} — using default score 50")
                from app.services.job_scorer import ScoreResult
                score_result = ScoreResult(score=50, reasoning="", key_matches=[], gaps=[])

            cover = ""
            if score_result.score >= settings.cover_letter_score_threshold:
                try:
                    cover = await generate_cover_letter(
                        profile_dict,
                        {"title": raw.title, "company": raw.company, "description": raw.description},
                        score_result.reasoning,
                        score_result.key_matches,
                    )
                except Exception as e:
                    logger.warning(f"Cover letter failed for '{raw.title}': {e}")

            job = Job(
                external_id=ext_id,
                source=raw.source,
                title=raw.title,
                company=raw.company,
                location=raw.location,
                description=raw.description,
                url=raw.url,
                posted_date=raw.posted_date,
                salary_range=raw.salary_range,
                is_remote=raw.is_remote,
                match_score=score_result.score,
                score_reasoning=score_result.reasoning,
                cover_letter=cover,
            )
            db.add(job)
            total_new += 1

        await db.commit()
        logger.info(f"Pipeline done — {total_found} found, {filtered_out} filtered, {total_new} new saved to DB")
        return {"jobs_found": total_found, "jobs_new": total_new, "jobs_filtered": filtered_out}


def run_scrape_sync(profile_id: str, portals: list[str]):
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(run_scrape_pipeline(profile_id, portals))
    except Exception as e:
        logger.error(f"Scheduled scrape failed: {e}")
    finally:
        loop.close()

