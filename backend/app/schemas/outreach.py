import uuid
from datetime import datetime

from pydantic import BaseModel


class OutreachContactResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    name: str | None
    title: str | None
    email: str | None
    linkedin_url: str | None
    source: str | None
    email_sent: bool
    email_sent_at: datetime | None
    email_subject: str | None
    email_body: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SendEmailRequest(BaseModel):
    subject: str
    body: str
