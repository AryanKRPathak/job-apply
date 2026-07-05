import uuid
from datetime import datetime

from pydantic import BaseModel, field_validator


class ProfileCreate(BaseModel):
    full_name: str
    email: str | None = None
    phone: str | None = None
    target_titles: list[str] = []
    target_locations: list[str] = []
    skills: list[str] = []
    years_exp: int | None = None
    story: str | None = None
    resume_text: str | None = None
    resume_filename: str | None = None
    company_blacklist: list[str] = []
    company_whitelist: list[str] = []
    title_keyword_blacklist: list[str] = []
    min_salary: int | None = None


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    target_titles: list[str] | None = None
    target_locations: list[str] | None = None
    skills: list[str] | None = None
    years_exp: int | None = None
    story: str | None = None
    company_blacklist: list[str] | None = None
    company_whitelist: list[str] | None = None
    title_keyword_blacklist: list[str] | None = None
    min_salary: int | None = None


class ProfileResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    resume_text: str | None
    resume_filename: str | None
    target_titles: list[str]
    target_locations: list[str]
    skills: list[str]
    years_exp: int | None
    story: str | None
    company_blacklist: list[str]
    company_whitelist: list[str]
    title_keyword_blacklist: list[str]
    min_salary: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("target_titles", "target_locations", "skills",
                     "company_blacklist", "company_whitelist", "title_keyword_blacklist",
                     mode="before")
    @classmethod
    def coerce_none_to_list(cls, v):
        return v if v is not None else []


class ResumeUploadResponse(BaseModel):
    extracted_text: str
    detected_skills: list[str]
    filename: str
    full_name: str = ""
    email: str = ""
    phone: str = ""
    years_exp: int | None = None
    story: str = ""
    suggested_titles: list[str] = []
