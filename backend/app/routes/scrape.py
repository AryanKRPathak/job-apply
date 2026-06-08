import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.profile import CandidateProfile
from app.models.schedule import ScrapeLog
from app.workers.scrape_task import run_scrape_pipeline

router = APIRouter()

ALL_PORTALS = ["indeed", "linkedin", "naukri"]

# In-memory task tracker {task_id: {"state": ..., "result": ..., "error": ...}}
_tasks: dict[str, dict[str, Any]] = {}


async def _run_and_track(task_id: str, profile_id: str, portals: list[str]):
    _tasks[task_id] = {"state": "RUNNING", "result": None, "error": None}
    try:
        result = await run_scrape_pipeline(profile_id, portals)
        _tasks[task_id] = {"state": "SUCCESS", "result": result, "error": None}
    except Exception as e:
        _tasks[task_id] = {"state": "FAILURE", "result": None, "error": str(e)}


@router.post("/now")
async def scrape_now(
    portals: list[str] | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CandidateProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=400, detail="Create a profile first")

    task_id = str(uuid.uuid4())
    asyncio.create_task(
        _run_and_track(task_id, str(profile.id), portals or ALL_PORTALS)
    )
    return {"task_id": task_id, "status": "queued"}


@router.get("/status")
async def scrape_status(task_id: str):
    task = _tasks.get(task_id)
    if not task:
        return {"task_id": task_id, "state": "PENDING", "result": None, "error": None}
    return {"task_id": task_id, **task}


@router.get("/logs")
async def scrape_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ScrapeLog).order_by(ScrapeLog.started_at.desc()).limit(50)
    )
    return result.scalars().all()
