# Job Apply — How to Run

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker Desktop (for Postgres + Redis)

---

## 1. Start infrastructure

```bash
cd job-apply
docker compose up -d
```

---

## 2. Backend setup

```bash
cd backend

# Copy env file and fill in your API keys
cp .env.example .env

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Run database migrations
alembic upgrade head

# Start API server
uvicorn main:app --reload --port 8000
```

---

## 3. Start Celery worker + beat scheduler

Open two additional terminals (with venv activated):

```bash
# Terminal 2 — Celery worker
celery -A app.workers.celery_app worker -Q scraping -c 2 --loglevel=info

# Terminal 3 — Celery beat (for scheduled scraping)
celery -A app.workers.celery_app beat -S redbeat.RedBeatScheduler --loglevel=info
```

---

## 4. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

---

## Required API Keys (set in backend/.env)

| Key | Where to get it |
|-----|----------------|
| `GEMINI_API_KEY` | https://aistudio.google.com/app/apikey |
| `DECODO_API_KEY` | https://decodo.com (optional — Playwright fallback works without it) |
| `SMTP_USER` / `SMTP_PASSWORD` | Gmail app password for outreach emails |

---

## Workflow

1. Go to **Profile** → upload your resume PDF → fill in job titles, locations, story → Save
2. Go to **Dashboard** → click **Scrape Now**
3. Watch jobs populate with match scores and AI cover letters
4. Click any job to read the full listing and edit the cover letter
5. Use the status dropdown to track applications
6. Go to **Outreach** on a job to find hiring manager contacts and send cold emails
7. Go to **Schedule** to set up automatic recurring scrapes
