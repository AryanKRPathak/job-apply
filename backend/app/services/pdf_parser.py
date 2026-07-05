import re
from dataclasses import dataclass, field

import fitz  # PyMuPDF


SKILL_KEYWORDS = [
    "python", "javascript", "typescript", "react", "node.js", "fastapi", "django", "flask",
    "java", "spring", "kotlin", "swift", "go", "rust", "c++", "c#", ".net",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ci/cd",
    "machine learning", "deep learning", "pytorch", "tensorflow", "scikit-learn",
    "data analysis", "pandas", "numpy", "spark", "kafka",
    "rest api", "graphql", "microservices", "system design",
    "git", "linux", "bash", "html", "css", "tailwind",
    # PM-specific
    "product management", "product roadmap", "agile", "scrum", "jira", "confluence",
    "user research", "a/b testing", "okrs", "kpis", "stakeholder management",
    "figma", "wireframing", "market research", "go-to-market", "growth",
]

# Common non-name first lines to skip
_SKIP_LINES = {"resume", "curriculum vitae", "cv", "profile", "summary", "objective"}


@dataclass
class ResumeData:
    extracted_text: str
    detected_skills: list[str]
    filename: str
    full_name: str = ""
    email: str = ""
    phone: str = ""
    years_exp: int | None = None
    story: str = ""
    suggested_titles: list[str] = field(default_factory=list)


def _extract_email(text: str) -> str:
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return m.group(0) if m else ""


def _extract_phone(text: str) -> str:
    # Matches +91 98765 43210, (123) 456-7890, 9876543210, etc.
    m = re.search(r"(\+?\d[\d\s\-().]{7,}\d)", text)
    if m:
        candidate = m.group(0).strip()
        digits = re.sub(r"\D", "", candidate)
        if 7 <= len(digits) <= 15:
            return candidate
    return ""


def _extract_name(text: str, email: str) -> str:
    """Best-effort: first non-empty line that looks like a name."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:8]:
        low = line.lower()
        # Skip if it contains email, URL, digits run, or known header words
        if email and email.lower() in low:
            continue
        if re.search(r"https?://|www\.", low):
            continue
        if low in _SKIP_LINES:
            continue
        if re.search(r"\d{4,}", line):  # long digit sequence = not a name
            continue
        # Name-like: 2-4 words, each capitalized, no special chars except hyphens
        words = line.split()
        if 2 <= len(words) <= 5 and all(re.match(r"^[A-Z][a-zA-Z\-'\.]+$", w) for w in words):
            return line
    return ""


def _extract_years_exp(text: str) -> int | None:
    """Look for explicit 'X years' mentions."""
    m = re.search(r"(\d+)\+?\s+years?\s+(of\s+)?(experience|exp)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # Count unique years in date ranges like 2019 - 2023
    years = re.findall(r"\b(20\d{2}|19\d{2})\b", text)
    if len(years) >= 2:
        years_int = sorted(set(int(y) for y in years))
        span = years_int[-1] - years_int[0]
        if 1 <= span <= 40:
            return span
    return None


def extract_resume(pdf_bytes: bytes, filename: str) -> ResumeData:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_text = [page.get_text() for page in doc]
        doc.close()
        full_text = "\n".join(pages_text)
    except Exception:
        # Fallback: try opening without specifying filetype
        try:
            doc = fitz.open(stream=pdf_bytes)
            pages_text = [page.get_text() for page in doc]
            doc.close()
            full_text = "\n".join(pages_text)
        except Exception as e:
            # If PDF is completely unreadable, return empty but don't crash
            full_text = ""

    lower_text = full_text.lower()
    skills = [skill for skill in SKILL_KEYWORDS if skill in lower_text]

    email = _extract_email(full_text)
    phone = _extract_phone(full_text)
    name = _extract_name(full_text, email)
    years_exp = _extract_years_exp(full_text)

    return ResumeData(
        extracted_text=full_text,
        detected_skills=skills,
        filename=filename,
        full_name=name,
        email=email,
        phone=phone,
        years_exp=years_exp,
    )


async def parse_resume_with_ai(resume_text: str, detected_skills: list[str], base: ResumeData) -> dict:
    """Use Gemini Flash to enrich the already-extracted data with story + suggested titles."""
    from app.services.gemini_client import generate_json
    from loguru import logger

    prompt = f"""You are a resume parser. Extract the following from this resume and return ONLY a JSON object:

{{
  "full_name": "person's full name, or empty string if not found",
  "email": "email address, or empty string",
  "phone": "phone number, or empty string",
  "years_exp": <integer total years of work experience, or null>,
  "skills": ["list of up to 20 key skills"],
  "story": "2-3 sentence first-person professional summary for cover letters. Be specific to their actual experience and achievements.",
  "suggested_titles": ["2-3 realistic job titles they should apply for based on their background"]
}}

Already detected: name={base.full_name!r}, email={base.email!r}, phone={base.phone!r}, years={base.years_exp}
Already found skills: {detected_skills}

Resume (first 3000 chars):
{resume_text[:3000]}

Return ONLY valid JSON, no markdown, no explanation."""

    try:
        result = await generate_json(prompt)
        return {
            "full_name": str(result.get("full_name") or base.full_name or ""),
            "email": str(result.get("email") or base.email or ""),
            "phone": str(result.get("phone") or base.phone or ""),
            "years_exp": int(result["years_exp"]) if result.get("years_exp") else base.years_exp,
            "skills": list(result.get("skills") or detected_skills),
            "story": str(result.get("story") or ""),
            "suggested_titles": list(result.get("suggested_titles") or []),
        }
    except Exception as e:
        logger.warning(f"AI resume parsing failed ({e}), using regex-extracted data")
        return {
            "full_name": base.full_name,
            "email": base.email,
            "phone": base.phone,
            "years_exp": base.years_exp,
            "skills": detected_skills,
            "story": "",
            "suggested_titles": [],
        }


