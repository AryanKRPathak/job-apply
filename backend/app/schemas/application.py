import uuid
from datetime import datetime

from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    job_id: uuid.UUID
    profile_id: uuid.UUID
    status: str = "saved"
    cover_letter_used: str | None = None
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None
    cover_letter_used: str | None = None
    outcome: str | None = None
    interview_date: datetime | None = None
    outcome_date: datetime | None = None
    feedback: str | None = None


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    profile_id: uuid.UUID
    status: str
    applied_at: datetime | None
    cover_letter_used: str | None
    notes: str | None
    outcome: str | None
    interview_date: datetime | None
    outcome_date: datetime | None
    feedback: str | None
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
