import re
from dataclasses import dataclass

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
]


@dataclass
class ResumeData:
    extracted_text: str
    detected_skills: list[str]
    filename: str


def extract_resume(pdf_bytes: bytes, filename: str) -> ResumeData:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = [page.get_text() for page in doc]
    doc.close()

    full_text = "\n".join(pages_text)
    lower_text = full_text.lower()

    skills = [skill for skill in SKILL_KEYWORDS if skill in lower_text]

    return ResumeData(
        extracted_text=full_text,
        detected_skills=skills,
        filename=filename,
    )
