import uuid
from datetime import date, datetime

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: uuid.UUID
    external_id: str
    source: str
    title: str
    company: str
    location: str | None
    description: str | None
    url: str
    posted_date: date | None
    scraped_at: datetime
    match_score: int | None
    score_reasoning: str | None
    cover_letter: str | None
    is_remote: bool
    salary_range: str | None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    page: int
    limit: int


class CoverLetterUpdate(BaseModel):
    cover_letter: str
