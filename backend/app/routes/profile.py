import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.profile import CandidateProfile
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate, ResumeUploadResponse
from app.services.pdf_parser import extract_resume, parse_resume_with_ai

router = APIRouter()


@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    from loguru import logger
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    try:
        content = await file.read()
        result = extract_resume(content, file.filename)
        logger.info(f"Resume extracted: {len(result.extracted_text)} chars, {len(result.detected_skills)} skills, name={result.full_name!r}")
        ai_data = await parse_resume_with_ai(result.extracted_text, result.detected_skills, result)
        logger.info(f"Final: name={ai_data['full_name']!r}, email={ai_data['email']!r}, years={ai_data['years_exp']}")
        return ResumeUploadResponse(
            extracted_text=result.extracted_text,
            detected_skills=ai_data["skills"],
            filename=result.filename,
            full_name=ai_data["full_name"],
            email=ai_data["email"],
            phone=ai_data["phone"],
            years_exp=ai_data["years_exp"],
            story=ai_data["story"],
            suggested_titles=ai_data["suggested_titles"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Resume upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ProfileResponse)
async def create_or_update_profile(data: ProfileCreate, db: AsyncSession = Depends(get_db)):
    from loguru import logger
    try:
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
    except Exception as e:
        logger.exception(f"Profile save failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
