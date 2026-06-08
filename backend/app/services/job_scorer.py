from dataclasses import dataclass

from loguru import logger

from app.services.gemini_client import generate_json


@dataclass
class ScoreResult:
    score: int
    reasoning: str
    key_matches: list[str]
    gaps: list[str]


async def score_job(profile: dict, job: dict) -> ScoreResult:
    prompt = f"""You are an expert recruiter evaluating job fit.

CANDIDATE PROFILE:
- Target titles: {", ".join(profile.get("target_titles") or [])}
- Skills: {", ".join(profile.get("skills") or [])}
- Years of experience: {profile.get("years_exp", "unknown")}
- Target locations: {", ".join(profile.get("target_locations") or [])}
- Career story: {(profile.get("story") or "")[:500]}

JOB POSTING:
Title: {job.get("title")}
Company: {job.get("company")}
Location: {job.get("location")}
Description: {(job.get("description") or "")[:3000]}

Score this job from 0 to 100 for fit, where:
- 80-100: Strong match, candidate should apply
- 50-79: Moderate match, worth reviewing
- 0-49: Poor match

Respond ONLY with valid JSON, no markdown:
{{
  "score": <integer 0-100>,
  "reasoning": "<2-3 sentence explanation>",
  "key_matches": ["<matched skill or keyword>"],
  "gaps": ["<requirement candidate may lack>"]
}}"""

    try:
        data = await generate_json(prompt)
        return ScoreResult(
            score=int(data.get("score", 50)),
            reasoning=data.get("reasoning", ""),
            key_matches=data.get("key_matches", []),
            gaps=data.get("gaps", []),
        )
    except Exception as e:
        logger.warning(f"Scoring failed for {job.get('title')} at {job.get('company')}: {e}")
        return ScoreResult(score=50, reasoning="Could not parse AI response", key_matches=[], gaps=[])
