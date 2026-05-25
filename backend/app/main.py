from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app import store
from app.schemas import (
    ChartPoint,
    DashboardSummary,
    Opportunity,
    SettingsUpdate,
    Trade,
    UserSettings,
)

app = FastAPI(
    title="Tax-Loss Harvesting API",
    version="0.1.0",
    description="Backend API for the Tax-Loss Harvesting dashboard.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/dashboard", response_model=DashboardSummary)
def dashboard() -> dict:
    return store.get_dashboard_summary()


@app.get("/api/v1/trades", response_model=list[Trade])
def trades(
    search: str | None = Query(default=None, description="Ticker text to search"),
    status: Literal["Completed", "Pending"] | None = Query(default=None),
) -> list[dict]:
    return store.get_trades(search=search, status=status)


@app.get("/api/v1/tax-alpha", response_model=list[ChartPoint])
def tax_alpha(timeframe: Literal["1Y", "5Y"] = "5Y") -> list[dict]:
    return store.TAX_ALPHA[timeframe]


@app.get("/api/v1/opportunities", response_model=list[Opportunity])
def opportunities() -> list[dict]:
    return store.OPPORTUNITIES


@app.get("/api/v1/settings", response_model=UserSettings)
def settings() -> dict:
    return store.SETTINGS


@app.patch("/api/v1/settings", response_model=UserSettings)
def update_settings(payload: SettingsUpdate) -> dict:
    updates = payload.model_dump(by_alias=True, exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No settings were provided.")

    store.SETTINGS.update(updates)
    return store.SETTINGS
