from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.database import engine
from app.scheduler import scheduler
from app.routes import applications, jobs, outreach, profile, question_bank, schedule, scrape


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting job-apply backend")
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    scheduler.start()
    logger.info("APScheduler started")
    yield
    scheduler.shutdown(wait=False)
    await app.state.http_client.aclose()
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(title="Job Apply API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(scrape.router, prefix="/api/scrape", tags=["scrape"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])
app.include_router(schedule.router, prefix="/api/schedule", tags=["schedule"])
app.include_router(outreach.router, prefix="/api/outreach", tags=["outreach"])
app.include_router(question_bank.router, prefix="/api/question-bank", tags=["question-bank"])


@app.get("/health")
async def health():
    return {"status": "ok"}
