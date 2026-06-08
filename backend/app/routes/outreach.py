import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.job import Job
from app.models.outreach import OutreachContact
from app.schemas.outreach import OutreachContactResponse, SendEmailRequest
from app.services.email_sender import send_email
from app.scrapers.career_page_scraper import scrape_career_contacts
from app.scrapers.apify_scraper import ApifyScraper
from app.config import settings

router = APIRouter()


@router.post("/find-contacts", response_model=list[OutreachContactResponse])
async def find_contacts(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    contacts = []

    # Try Apify LinkedIn recruiter search
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            scraper = ApifyScraper(client)
            items = await scraper._run_actor(
                "harvestapi/linkedin-profile-search",
                {
                    "keyword": f"recruiter {job.company}",
                    "title": "Recruiter HR Talent",
                    "limit": 5,
                },
            )
            for item in items:
                contacts.append({
                    "name": item.get("fullName"),
                    "title": item.get("headline"),
                    "email": item.get("email"),
                    "linkedin_url": item.get("profileUrl"),
                    "source": "linkedin",
                })
    except Exception:
        pass

    # Try company website
    if job.url:
        website_contacts = await scrape_career_contacts(job.url, job.company or "")
        contacts.extend(website_contacts)

    saved = []
    for c in contacts:
        if not c.get("email") and not c.get("linkedin_url"):
            continue
        existing = await db.execute(
            select(OutreachContact).where(
                OutreachContact.job_id == job_id,
                OutreachContact.email == c.get("email"),
            )
        )
        if existing.scalar_one_or_none():
            continue
        contact = OutreachContact(job_id=job_id, **c)
        db.add(contact)
        saved.append(contact)

    await db.commit()
    for c in saved:
        await db.refresh(c)
    return saved


@router.get("/{job_id}", response_model=list[OutreachContactResponse])
async def list_contacts(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OutreachContact).where(OutreachContact.job_id == job_id)
    )
    return result.scalars().all()


@router.post("/{contact_id}/send", response_model=OutreachContactResponse)
async def send_outreach(contact_id: uuid.UUID, data: SendEmailRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OutreachContact).where(OutreachContact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if not contact.email:
        raise HTTPException(status_code=400, detail="No email address for this contact")

    await send_email(to=contact.email, subject=data.subject, body=data.body)

    from datetime import datetime, timezone
    contact.email_sent = True
    contact.email_sent_at = datetime.now(timezone.utc)
    contact.email_subject = data.subject
    contact.email_body = data.body
    await db.commit()
    await db.refresh(contact)
    return contact
