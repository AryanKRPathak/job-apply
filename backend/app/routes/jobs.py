import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.job import Job
from app.schemas.job import CoverLetterUpdate, JobListResponse, JobResponse

router = APIRouter()


@router.get("", response_model=JobListResponse)
async def list_jobs(
    score_min: int | None = Query(None),
    location: str | None = Query(None),
    company: str | None = Query(None),
    source: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Job)
    if score_min is not None:
        query = query.where(Job.match_score >= score_min)
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))
    if company:
        query = query.where(Job.company.ilike(f"%{company}%"))
    if source:
        query = query.where(Job.source == source)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.order_by(Job.match_score.desc().nullslast(), Job.scraped_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return JobListResponse(items=list(items), total=total, page=page, limit=limit)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.patch("/{job_id}/cover-letter", response_model=JobResponse)
async def update_cover_letter(job_id: uuid.UUID, data: CoverLetterUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.cover_letter = data.cover_letter
    await db.commit()
    await db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
async def delete_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.delete(job)
    await db.commit()
