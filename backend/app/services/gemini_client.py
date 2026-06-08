import json
import re

import google.generativeai as genai
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

genai.configure(api_key=settings.gemini_api_key)

_flash = genai.GenerativeModel(settings.gemini_scoring_model)
_pro = genai.GenerativeModel(settings.gemini_writing_model)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_text(prompt: str, use_pro: bool = False) -> str:
    model = _pro if use_pro else _flash
    response = await model.generate_content_async(prompt)
    return response.text


async def generate_json(prompt: str) -> dict:
    raw = await generate_text(prompt, use_pro=False)
    # Strip markdown code fences if present
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-z]*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning("Gemini returned non-JSON, attempting extraction")
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from Gemini response: {cleaned[:200]}")
