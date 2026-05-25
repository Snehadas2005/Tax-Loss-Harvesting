from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone


TRADES = [
    {
        "id": 1,
        "date": "Nov 15, 2023",
        "sold": "INFY.NS",
        "bought": "TCS.NS",
        "taxSaved": 4500,
        "status": "Completed",
        "reason": "INFY dropped 8% below cost basis. Swapped to TCS to maintain IT sector exposure.",
        "fees": 15.50,
        "lossPercent": 8.0,
        "washSaleSafe": True,
    },
    {
        "id": 2,
        "date": "Oct 02, 2023",
        "sold": "HDFCBANK.NS",
        "bought": "ICICIBANK.NS",
        "taxSaved": 12000,
        "status": "Completed",
        "reason": "HDFCBANK stayed below cost basis while ICICIBANK preserved banking exposure.",
        "fees": 22.00,
        "lossPercent": 11.4,
        "washSaleSafe": True,
    },
    {
        "id": 3,
        "date": "Aug 21, 2023",
        "sold": "RELIANCE.NS",
        "bought": "ONGC.NS",
        "taxSaved": 8500,
        "status": "Completed",
        "reason": "Energy sector rebalance captured a short-term loss without leaving the sector.",
        "fees": 18.75,
        "lossPercent": 5.0,
        "washSaleSafe": True,
    },
    {
        "id": 4,
        "date": "Jul 10, 2023",
        "sold": "WIPRO.NS",
        "bought": "HCLTECH.NS",
        "taxSaved": 3200,
        "status": "Completed",
        "reason": "Momentum signal flagged WIPRO as a stagnant loser versus its IT peer basket.",
        "fees": 12.00,
        "lossPercent": 6.2,
        "washSaleSafe": True,
    },
    {
        "id": 5,
        "date": "Jun 05, 2023",
        "sold": "TCS.NS",
        "bought": "WIPRO.NS",
        "taxSaved": 2100,
        "status": "Pending",
        "reason": "Awaiting market open and final wash-sale window check before execution.",
        "fees": 0.00,
        "lossPercent": 3.1,
        "washSaleSafe": False,
    },
]

TAX_ALPHA = {
    "5Y": [
        {"year": "2019", "Standard": 100000, "Harvested": 100000},
        {"year": "2020", "Standard": 108000, "Harvested": 111500},
        {"year": "2021", "Standard": 125000, "Harvested": 132000},
        {"year": "2022", "Standard": 115000, "Harvested": 126000},
        {"year": "2023", "Standard": 135000, "Harvested": 149500},
    ],
    "1Y": [
        {"year": "Jan", "Standard": 126000, "Harvested": 126000},
        {"year": "Apr", "Standard": 128000, "Harvested": 131000},
        {"year": "Jul", "Standard": 131000, "Harvested": 138000},
        {"year": "Oct", "Standard": 129000, "Harvested": 142000},
        {"year": "Dec", "Standard": 135000, "Harvested": 149500},
    ],
}

OPPORTUNITIES = [
    {
        "ticker": "LTIM.NS",
        "replacement": "TECHM.NS",
        "unrealizedLoss": 18500,
        "lossPercent": 9.8,
        "estimatedTaxSaving": 3700,
        "confidence": 0.82,
        "rationale": "Similar IT services exposure with weaker recent recovery score on the current holding.",
    },
    {
        "ticker": "AXISBANK.NS",
        "replacement": "KOTAKBANK.NS",
        "unrealizedLoss": 26300,
        "lossPercent": 7.4,
        "estimatedTaxSaving": 5260,
        "confidence": 0.78,
        "rationale": "Banking sector pair keeps beta close while realizing the current drawdown.",
    },
    {
        "ticker": "TATAMOTORS.NS",
        "replacement": "M&M.NS",
        "unrealizedLoss": 14200,
        "lossPercent": 6.1,
        "estimatedTaxSaving": 2840,
        "confidence": 0.73,
        "rationale": "Auto-sector replacement candidate with lower wash-sale similarity risk.",
    },
]

SETTINGS = {
    "name": "Ansh Jaiswal",
    "email": "ansh.jaiswal@example.com",
    "role": "Lead Frontend Engineer",
    "harvestingAlerts": True,
    "riskProfile": "Balanced",
}


def get_trades(search: str | None = None, status: str | None = None) -> list[dict]:
    trades = deepcopy(TRADES)

    if search:
        query = search.casefold()
        trades = [
            trade
            for trade in trades
            if query in trade["sold"].casefold() or query in trade["bought"].casefold()
        ]

    if status:
        trades = [trade for trade in trades if trade["status"].casefold() == status.casefold()]

    return trades


def get_dashboard_summary() -> dict:
    completed_trades = [trade for trade in TRADES if trade["status"] == "Completed"]
    total_tax_saved = sum(trade["taxSaved"] for trade in completed_trades)
    active_opportunities = len(OPPORTUNITIES) + len(
        [trade for trade in TRADES if trade["status"] == "Pending"]
    )

    harvested_end = TAX_ALPHA["5Y"][-1]["Harvested"]
    standard_end = TAX_ALPHA["5Y"][-1]["Standard"]
    alpha = ((harvested_end - standard_end) / standard_end) * 100

    return {
        "stats": [
            {
                "title": "Total Tax Saved",
                "value": f"Rs. {total_tax_saved:,.0f}",
                "trend": "+12%",
                "trendType": "positive",
            },
            {
                "title": "Harvesting Alpha",
                "value": f"{alpha:.1f}%",
                "trend": "+0.5%",
                "trendType": "positive",
            },
            {
                "title": "Active Opportunities",
                "value": f"{active_opportunities} Stocks",
                "trend": "-2",
                "trendType": "negative",
            },
        ],
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
