---
title: TaxLossHarvest
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Tax-Loss Harvesting Backend

FastAPI service for the dashboard. It ships with seed data so the frontend can run immediately, while keeping the API shape ready for a database or ML integration later.

## Run locally

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## API

- `GET /health`
- `GET /api/v1/dashboard`
- `GET /api/v1/trades?search=INFY&status=Completed`
- `GET /api/v1/tax-alpha?timeframe=5Y`
- `GET /api/v1/opportunities`
- `GET /api/v1/settings`
- `PATCH /api/v1/settings`

Interactive docs are available at `http://127.0.0.1:8000/docs` while the server is running.
