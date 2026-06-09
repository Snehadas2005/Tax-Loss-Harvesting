const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export interface SettingsUpdatePayload {
  harvestingAlerts?: boolean;
  riskProfile?: "Conservative" | "Balanced" | "Aggressive";
  name?: string;
  email?: string;
  role?: string;
}

export interface PortfolioAssetPayload {
  ticker: string;
  purchasePrice: number;
  currentPrice: number;
}

const handleResponse = async (r: Response) => {
  if (!r.ok) {
    const errorText = await r.text();
    throw new Error(errorText || `HTTP error! Status: ${r.status}`);
  }
  return r.json();
};

export const api = {
  dashboard:     () => fetch(`${BASE}/api/v1/dashboard`).then(handleResponse),
  taxAlpha:  (tf: "1Y"|"5Y") => fetch(`${BASE}/api/v1/tax-alpha?timeframe=${tf}`).then(handleResponse),
  trades:    (search="", status="") => {
    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (status) params.append("status", status);
    const qs = params.toString();
    return fetch(`${BASE}/api/v1/trades${qs ? `?${qs}` : ""}`).then(handleResponse);
  },
  opportunities: () => fetch(`${BASE}/api/v1/opportunities`).then(handleResponse),
  settings:      () => fetch(`${BASE}/api/v1/settings`).then(handleResponse),
  updateSettings: (payload: SettingsUpdatePayload) => fetch(`${BASE}/api/v1/settings`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }).then(handleResponse),
  backtest:  (cap?: number, rate?: number) => {
    const query = cap !== undefined || rate !== undefined 
      ? `?initial_capital=${cap ?? 100000}&tax_rate=${rate ?? 0.15}` 
      : "";
    return fetch(`${BASE}/api/v1/backtest${query}`).then(handleResponse);
  },
  recommend: (portfolio: PortfolioAssetPayload[]) => fetch(`${BASE}/api/v1/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ portfolio })
  }).then(handleResponse),
};