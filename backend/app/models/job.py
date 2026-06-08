import uuid
from datetime import date, datetime
from typing import Optional


from sqlalchemy import Boolean, Date, DateTime, Integer, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("external_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    company: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    url: Mapped[str] = mapped_column(Text, nullable=False)
    posted_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    match_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    score_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    salary_range: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

