import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ARRAY, DateTime, Integer, String, Text, func

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resume_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resume_filename: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_titles: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    target_locations: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    skills: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    years_exp: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    story: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Feature 1: company filters
    company_blacklist: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    company_whitelist: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Feature 3: title keyword blacklist
    title_keyword_blacklist: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Feature 4: salary floor
    min_salary: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
