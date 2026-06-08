import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationResponse, ApplicationUpdate

router = APIRouter()


@router.post("", response_model=ApplicationResponse, status_code=201)
async def create_application(data: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    app = Application(**data.model_dump())
    if data.status == "applied":
        app.applied_at = datetime.utcnow()
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).order_by(Application.created_at.desc()))
    return result.scalars().all()


@router.patch("/{app_id}", response_model=ApplicationResponse)
async def update_application(app_id: uuid.UUID, data: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    if data.status == "applied" and not app.applied_at:
        app.applied_at = datetime.utcnow()
    await db.commit()
    await db.refresh(app)
    return app
