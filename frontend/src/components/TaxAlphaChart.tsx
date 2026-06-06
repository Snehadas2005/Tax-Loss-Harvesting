"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Loader2 } from "lucide-react";

export default function TaxAlphaChart() {
  const [timeframe, setTimeframe] = useState<"1Y" | "5Y">("5Y");
  const [fullData, setFullData] = useState<any[]>([]);
  const [currentData, setCurrentData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    api.backtest()
      .then((res) => {
        if (res && res.time_series_chart_data) {
          setFullData(res.time_series_chart_data);
        }
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch backtest data", err);
        setIsLoading(false);
      });
  }, []);

  useEffect(() => {
    if (fullData.length === 0) return;

    let rendered = fullData;
    if (timeframe === "1Y") {
      // Approximate 252 trading days for 1 year
      rendered = fullData.slice(-252);
    }

    // Downsample chart data to at most 150 points for smooth Recharts rendering
    const maxPoints = 150;
    const step = Math.max(1, Math.floor(rendered.length / maxPoints));
    const downsampled = rendered.filter((_, idx) => idx % step === 0);
    setCurrentData(downsampled);
  }, [fullData, timeframe]);

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 mt-6 transition-colors duration-200">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-lg font-bold text-slate-800 dark:text-white">
            Tax Alpha Generation
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Portfolio value: Standard vs. Harvested over time (ML Simulated Backtest)
          </p>
        </div>

        <div className="flex bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
          <button
            onClick={() => setTimeframe("1Y")}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
              timeframe === "1Y"
                ? "bg-white dark:bg-slate-700 text-slate-800 dark:text-white shadow-sm"
                : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
            }`}
          >
            1 Year
          </button>
          <button
            onClick={() => setTimeframe("5Y")}
            className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
              timeframe === "5Y"
                ? "bg-white dark:bg-slate-700 text-slate-800 dark:text-white shadow-sm"
                : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
            }`}
          >
            5 Years
          </button>
        </div>
      </div>

      <div className="h-[300px] w-full mt-4 flex items-center justify-center">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center gap-2">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Running backtest simulation on ML Engine...
            </p>
          </div>
        ) : currentData.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={currentData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="colorHarvested" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorStandard" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#94a3b8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#e2e8f0"
                strokeOpacity={0.5}
              />
              <XAxis
                dataKey="date"
                stroke="#64748b"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#64748b"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: "8px",
                  border: "none",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                }}
                labelFormatter={(label) => `Date: ${label}`}
                formatter={(value: any) => [`₹${Number(value).toLocaleString()}`, ""]}
              />
              <Area
                type="monotone"
                name="Buy & Hold (Standard)"
                dataKey="baseline_value"
                stroke="#94a3b8"
                fillOpacity={1}
                fill="url(#colorStandard)"
              />
              <Area
                type="monotone"
                name="Harvested Engine (Active)"
                dataKey="active_value"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#colorHarvested)"
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-slate-500 dark:text-slate-400">
            No chart data available.
          </p>
        )}
      </div>
    </div>
  );
}
