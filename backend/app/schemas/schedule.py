import uuid
from datetime import datetime

from pydantic import BaseModel


class ScheduleCreate(BaseModel):
    profile_id: uuid.UUID
    cron_expression: str
    portals: list[str] = ["indeed", "linkedin", "naukri"]


class ScheduleUpdate(BaseModel):
    cron_expression: str | None = None
    portals: list[str] | None = None
    is_active: bool | None = None


class ScheduleResponse(BaseModel):
    id: uuid.UUID
    profile_id: uuid.UUID
    cron_expression: str
    portals: list[str] | None
    is_active: bool
    last_run_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ScrapeLogResponse(BaseModel):
    id: uuid.UUID
    schedule_id: uuid.UUID | None
    started_at: datetime
    finished_at: datetime | None
    status: str
    jobs_found: int
    jobs_new: int
    error_message: str | None

    model_config = {"from_attributes": True}
