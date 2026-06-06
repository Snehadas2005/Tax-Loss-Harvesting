const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export const api = {
  dashboard:     () => fetch(`${BASE}/api/v1/dashboard`).then(r => r.json()),
  taxAlpha:  (tf: "1Y"|"5Y") => fetch(`${BASE}/api/v1/tax-alpha?timeframe=${tf}`).then(r => r.json()),
  trades:    (search="", status="") => fetch(`${BASE}/api/v1/trades?search=${search}&status=${status}`).then(r => r.json()),
  opportunities: () => fetch(`${BASE}/api/v1/opportunities`).then(r => r.json()),
  settings:      () => fetch(`${BASE}/api/v1/settings`).then(r => r.json()),
  updateSettings: (payload: any) => fetch(`${BASE}/api/v1/settings`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }).then(r => r.json()),
  backtest:  (cap?: number, rate?: number) => {
    const query = cap !== undefined || rate !== undefined 
      ? `?initial_capital=${cap ?? 100000}&tax_rate=${rate ?? 0.15}` 
      : "";
    return fetch(`${BASE}/api/v1/backtest${query}`).then(r => r.json());
  },
  recommend: (portfolio: any[]) => fetch(`${BASE}/api/v1/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ portfolio })
  }).then(r => r.json()),
};