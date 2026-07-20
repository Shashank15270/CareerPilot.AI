# CareerPilot.AI

AI-powered job recommendation platform. Upload your resume, get matched to live Indian job listings, and receive AI analysis for each role — match explanation, ATS score, skill gap, and interview prep.

**Stack:** FastAPI + SQLAlchemy (backend) · React + Vite + Tailwind (frontend) · JSearch API (jobs) · Groq (AI)

---

## Setup

### 1. Get the code

```bash
git clone https://github.com/Shashank15270/CareerPilot.AI.git
cd CareerPilot.AI
```

### 2. Create `backend/.env`

This is **the only file you need to add.** Copy the template:

```bash
cd backend
cp .env.example .env
```

Then open `backend/.env` and fill in two keys:

| Key | Where to get it |
|---|---|
| `RAPIDAPI_KEY` | [JSearch on RapidAPI](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) — subscribe, then copy `X-RapidAPI-Key` |
| `GROQ_API_KEY` | [console.groq.com/keys](https://console.groq.com/keys) |

Leave `SECRET_KEY` and `DATABASE_URL` as they are for local use.

### 3. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend runs at **http://localhost:8000** · API docs at **http://localhost:8000/docs**

> First AI request downloads the embedding model (~90 MB) and takes ~60s. After that it's cached.

### 4. Frontend

In a **second terminal**:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:3000**

---

## Using it

1. Open http://localhost:3000
2. Register an account
3. Go to **Scan & Recommendation**, upload a resume (PDF or DOCX)
4. Optionally set filters — city, experience level, skills
5. Expand any result card and use the **AI Career Coach** buttons

---

## Notes

- **Job search is India-only**, powered by JSearch. Pick a city from the dropdown or leave it as "All of India".
- **Restart the backend after editing `.env`** — keys are read once at startup.
- Results are ranked by **skills (60%) → experience (25%) → location (15%)**.
- **Smart Fallbacks**: If no explicit search query is provided, the system automatically extracts your latest job title or top skills from the uploaded resume to fetch the most relevant jobs.
- Groq's free tier allows ~12k tokens/min. Clicking many AI buttons quickly may hit a rate limit; you'll see a message telling you how long to wait.
- A search takes ~10–30s (job fetch + embedding + ranking).

## Troubleshooting

| Problem | Fix |
|---|---|
| `503 RAPIDAPI_KEY is missing` | Add the key to `backend/.env` and restart the backend |
| AI buttons return an error | Check `GROQ_API_KEY`, then restart the backend |
| No jobs found | Confirm your RapidAPI account is **subscribed** to JSearch, not just registered |
| `python` not found (Windows) | Use `py` instead, or install Python from python.org |
