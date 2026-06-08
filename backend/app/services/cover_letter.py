from loguru import logger

from app.services.gemini_client import generate_text


async def generate_cover_letter(profile: dict, job: dict, score_reasoning: str, key_matches: list[str]) -> str:
    prompt = f"""You are a professional career coach writing a personalized cover letter.

CANDIDATE:
Name: {profile.get("full_name", "the candidate")}
Story: {profile.get("story", "")}
Key skills: {", ".join((profile.get("skills") or [])[:15])}
Years of experience: {profile.get("years_exp", "several")}

JOB:
Title: {job.get("title")}
Company: {job.get("company")}
Description: {(job.get("description") or "")[:4000]}
Score reasoning: {score_reasoning}
Key matches: {", ".join(key_matches)}

Write a compelling 3-paragraph cover letter (250-350 words) that:
1. Opens with a specific hook tied to the company or role — never start with "I am applying for"
2. Connects the candidate's story and 2-3 specific skills to the job's requirements
3. Closes with a clear call to action

Tone: professional but warm. No generic filler phrases.
Return ONLY the cover letter text, no subject line or extra metadata."""

    try:
        return await generate_text(prompt, use_pro=True)
    except Exception as e:
        logger.warning(f"Cover letter generation failed for {job.get('title')}: {e}")
        return ""
