from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate
from app.schemas.job import CoverLetterUpdate, JobListResponse, JobResponse
from app.schemas.outreach import OutreachContactResponse, SendEmailRequest
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate, ResumeUploadResponse
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate, ScrapeLogResponse

__all__ = [
    "ProfileCreate",
    "ProfileUpdate",
    "ProfileResponse",
    "ResumeUploadResponse",
    "JobResponse",
    "JobListResponse",
    "CoverLetterUpdate",
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    "ScheduleCreate",
    "ScheduleUpdate",
    "ScheduleResponse",
    "ScrapeLogResponse",
    "OutreachContactResponse",
    "SendEmailRequest",
]
