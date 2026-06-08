import uuid
from datetime import datetime

from pydantic import BaseModel


class QuestionBankCreate(BaseModel):
    profile_id: uuid.UUID
    question: str
    answer: str | None = None
    category: str | None = None


class QuestionBankUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    category: str | None = None


class QuestionBankResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    question: str
    answer: str | None
    category: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
