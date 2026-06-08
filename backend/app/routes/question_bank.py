import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.question_bank import QuestionBank
from app.schemas.question_bank import QuestionBankCreate, QuestionBankResponse, QuestionBankUpdate

router = APIRouter()


@router.post("", response_model=QuestionBankResponse, status_code=201)
async def create_question(data: QuestionBankCreate, db: AsyncSession = Depends(get_db)):
    q = QuestionBank(**data.model_dump())
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return q


@router.get("/{profile_id}", response_model=list[QuestionBankResponse])
async def list_questions(profile_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(QuestionBank)
        .where(QuestionBank.profile_id == profile_id)
        .order_by(QuestionBank.category, QuestionBank.created_at)
    )
    return result.scalars().all()


@router.patch("/{question_id}", response_model=QuestionBankResponse)
async def update_question(question_id: uuid.UUID, data: QuestionBankUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(QuestionBank).where(QuestionBank.id == question_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(q, field, value)
    await db.commit()
    await db.refresh(q)
    return q


@router.delete("/{question_id}", status_code=204)
async def delete_question(question_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(QuestionBank).where(QuestionBank.id == question_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    await db.delete(q)
    await db.commit()
