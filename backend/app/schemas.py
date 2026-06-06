from typing import Literal

from pydantic import BaseModel, Field


class StatCard(BaseModel):
    title: str
    value: str
    trend: str
    trend_type: Literal["positive", "negative"] = Field(alias="trendType")

    model_config = {"populate_by_name": True}


class DashboardSummary(BaseModel):
    stats: list[StatCard]
    generated_at: str = Field(alias="generatedAt")

    model_config = {"populate_by_name": True}


class Trade(BaseModel):
    id: int
    date: str
    sold: str
    bought: str
    tax_saved: float = Field(alias="taxSaved")
    status: Literal["Completed", "Pending"]
    reason: str
    fees: float
    loss_percent: float = Field(alias="lossPercent")
    wash_sale_safe: bool = Field(alias="washSaleSafe")

    model_config = {"populate_by_name": True}


class ChartPoint(BaseModel):
    year: str
    Standard: float
    Harvested: float


class Opportunity(BaseModel):
    ticker: str
    replacement: str
    unrealized_loss: float = Field(alias="unrealizedLoss")
    loss_percent: float = Field(alias="lossPercent")
    estimated_tax_saving: float = Field(alias="estimatedTaxSaving")
    confidence: float
    rationale: str

    model_config = {"populate_by_name": True}


class UserSettings(BaseModel):
    name: str
    email: str
    role: str
    harvesting_alerts: bool = Field(alias="harvestingAlerts")
    risk_profile: Literal["Conservative", "Balanced", "Aggressive"] = Field(alias="riskProfile")

    model_config = {"populate_by_name": True}


class SettingsUpdate(BaseModel):
    harvesting_alerts: bool | None = Field(default=None, alias="harvestingAlerts")
    risk_profile: Literal["Conservative", "Balanced", "Aggressive"] | None = Field(
        default=None,
        alias="riskProfile",
    )

    model_config = {"populate_by_name": True}


class PortfolioAsset(BaseModel):
    ticker: str = Field(..., example="AAPL")
    purchase_price: float = Field(..., description="The price at which the investor bought the stock", example=190.0, alias="purchasePrice")
    current_price: float = Field(..., description="The current market price of the asset", example=161.5, alias="currentPrice")

    model_config = {"populate_by_name": True}


class HarvestRequest(BaseModel):
    portfolio: list[PortfolioAsset]

