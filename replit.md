# Jira Excel Reporter

## Overview
A web app that accepts a Jira Excel/CSV export file and generates three aggregated reports (charts + tables) from the uploaded data — no Jira API connection required.

## Architecture

### Backend (Python / FastAPI)
- **Framework:** FastAPI + Uvicorn
- **Port:** 8000 (localhost only in dev)
- **Entry point:** `backend/app/main.py`
- **Key files:**
  - `backend/app/parser.py` — CSV/XLSX parsing with tolerant header matching
  - `backend/app/aggregator.py` — Pure aggregation logic for 3 reports
  - `backend/app/models.py` — Pydantic v2 response models
  - `backend/requirements.txt` — Python dependencies
- **Endpoints:**
  - `GET /healthz` — liveness check
  - `GET /api/sample` — download bundled sample XLSX
  - `POST /api/analyze` — multipart upload → JSON reports

### Frontend (React / Vite)
- **Framework:** React 18 + Vite 5
- **Port:** 5000 (0.0.0.0 for Replit proxy compatibility)
- **Charts:** Recharts
- **Entry point:** `frontend/src/`
- **Dev proxy:** `/api` → `http://localhost:8000`

## Workflows
- **Backend API** — `cd backend && uvicorn app.main:app --host localhost --port 8000 --reload` (console, port 8000)
- **Start application** — `cd frontend && npm run dev` (webview, port 5000)

## Deployment
- **Target:** autoscale
- **Build:** Build frontend → copy to `backend/app/static/`
- **Run:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 5000`
- Backend serves static frontend in production (SPA fallback configured)

## Key Configuration
- `frontend/vite.config.js` — `host: '0.0.0.0'`, `allowedHosts: true`, proxy to backend
- `backend/app/main.py` — CORS set to `allow_origins=["*"]` for Replit proxy compatibility
