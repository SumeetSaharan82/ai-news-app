# Briefed — AI News App

An Inshorts-style AI-powered news app. Swipe through personalized news briefs, one card at a time.

## Architecture

| Layer | Stack | Port |
|---|---|---|
| Backend | FastAPI + SQLite + JWT auth | 8000 |
| Frontend | React 18 + Vite + Tailwind CSS | 5173 (main preview) |

The Vite dev server proxies `/api/*` → `http://localhost:8000`.

## Running the app

Both workflows must be running:
- **Backend** – `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
- **Frontend** – `cd frontend-react && npm run dev`

Visit port **5173** to see the app.

## Features
- 🔐 JWT authentication (register / login)
- 📰 Inshorts-style full-screen swipe feed (CSS scroll-snap)
- 🎯 Personalized by category & region preferences
- 🌙 Premium dark mode UI with framer-motion animations
- 💰 Monetization-ready (upgrade modal with Pro/Premium tiers)
- 📱 Mobile-first PWA with bottom navigation

## Environment variables / Secrets
Set these in Replit Secrets for full functionality:
- `SECRET_KEY` — JWT signing secret (use `SESSION_SECRET` value)
- `NEWSAPI_KEY` — for NewsAPI.org news fetching
- `OPENAI_API_KEY` — for AI summaries
- `ANTHROPIC_API_KEY` — alternative LLM provider

## Monetization strategy
- **Free**: 15 articles/day
- **Pro** ($4.99/mo): Unlimited articles, region filters, bookmarks
- **Premium** ($9.99/mo): Everything + AI summaries, trend analysis, email digest
- Stripe integration ready (upgrade modal placeholder in `UpgradeModal.jsx`)

## User preferences
- Keep existing FastAPI backend structure
- Dark mode default, no light mode toggle needed
- Mobile-first, max-width centered on desktop
