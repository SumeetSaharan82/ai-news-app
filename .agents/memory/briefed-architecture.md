---
name: Briefed app architecture
description: Full-stack layout, ports, workflow names, and key integration points for the Briefed AI News app
---

## Stack
- **Backend**: FastAPI + SQLite (briefed.db) + JWT auth via PyJWT + passlib(pbkdf2_sha256)
- **Frontend**: React 18 + Vite 5 + Tailwind CSS 3 + Zustand + Framer Motion + React Router v6
- **Port layout**: Backend on 8000 (console workflow), Frontend on 5000 (webview workflow)
- **API proxy**: Vite proxies `/api/*` → `http://localhost:8000` in `frontend-react/vite.config.js`

## Workflow names
- `Backend API` — `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
- `Start application` — `cd frontend-react && npm run dev`

## Key directories
- Backend code: `backend/` (FastAPI app, routers in `backend/api/v1/`)
- Frontend: `frontend-react/src/` (pages/, components/, api/, store/)
- DB file: `briefed.db` (SQLite, auto-created)

## Monetization model
- Free: 15 articles/day, server-enforced via `backend/api/v1/usage.py`
- Pro ($4.99/mo) / Premium ($9.99/mo): unlimited, controlled by `tier` field in user preferences JSON
- Usage tracked per unique article per user per day in `preferences._usage` JSON column

**Why:** Kept monetization logic server-side to prevent client bypass.
**How to apply:** Any new article-gating logic should check `/api/v1/usage/status` and call `/api/v1/usage/record-read`.
