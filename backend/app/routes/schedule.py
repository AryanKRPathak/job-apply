import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schedule import ScrapeSchedule
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate

router = APIRouter()


def _sync_scheduler(schedule: ScrapeSchedule, delete: bool = False):
    """Add or remove a job from the APScheduler instance stored on app state."""
    try:
        from app.scheduler import scheduler
        job_id = f"schedule:{schedule.id}"

        if delete:
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
            return

        from app.workers.scrape_task import run_scrape_sync
        from apscheduler.triggers.cron import CronTrigger

        parts = schedule.cron_expression.split()
        if len(parts) != 5:
            return
        minute, hour, dom, month, dow = parts

        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)

        scheduler.add_job(
            run_scrape_sync,
            CronTrigger(minute=minute, hour=hour, day=dom, month=month, day_of_week=dow),
            id=job_id,
            args=[str(schedule.profile_id), schedule.portals or []],
            replace_existing=True,
        )
    except Exception as e:
        from loguru import logger
        logger.warning(f"Scheduler sync failed: {e}")


@router.post("", response_model=ScheduleResponse, status_code=201)
async def create_schedule(data: ScheduleCreate, db: AsyncSession = Depends(get_db)):
    schedule = ScrapeSchedule(**data.model_dump())
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    _sync_scheduler(schedule)
    return schedule


@router.get("", response_model=list[ScheduleResponse])
async def list_schedules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ScrapeSchedule).order_by(ScrapeSchedule.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: uuid.UUID, data: ScheduleUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ScrapeSchedule).where(ScrapeSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)
    await db.commit()
    await db.refresh(schedule)
    if schedule.is_active:
        _sync_scheduler(schedule)
    else:
        _sync_scheduler(schedule, delete=True)
    return schedule


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ScrapeSchedule).where(ScrapeSchedule.id == schedule_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    _sync_scheduler(schedule, delete=True)
    await db.delete(schedule)
    await db.commit()
