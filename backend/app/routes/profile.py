import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.profile import CandidateProfile
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate, ResumeUploadResponse
from app.services.pdf_parser import extract_resume

router = APIRouter()


@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    content = await file.read()
    result = extract_resume(content, file.filename)
    return result


@router.post("", response_model=ProfileResponse)
async def create_or_update_profile(data: ProfileCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CandidateProfile).limit(1))
    profile = result.scalar_one_or_none()
    if profile:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
    else:
        profile = CandidateProfile(**data.model_dump())
        db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.get("", response_model=ProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CandidateProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("", response_model=ProfileResponse)
async def patch_profile(data: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CandidateProfile).limit(1))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.commit()
    await db.refresh(profile)
    return profile
