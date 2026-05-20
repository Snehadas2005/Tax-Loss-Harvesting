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
import { useState } from "react";

const data5Years = [
  { year: "2019", Standard: 100000, Harvested: 100000 },
  { year: "2020", Standard: 108000, Harvested: 112000 },
  { year: "2021", Standard: 125000, Harvested: 132000 },
  { year: "2022", Standard: 115000, Harvested: 126000 },
  { year: "2023", Standard: 135000, Harvested: 150000 },
];

const data1Year = [
  { year: "Jan", Standard: 115000, Harvested: 115000 },
  { year: "Apr", Standard: 118000, Harvested: 121000 },
  { year: "Jul", Standard: 122000, Harvested: 128000 },
  { year: "Oct", Standard: 128000, Harvested: 139000 },
  { year: "Dec", Standard: 135000, Harvested: 150000 },
];

export default function TaxAlphaChart() {
  const [timeframe, setTimeframe] = useState<"1Y" | "5Y">("5Y");
  const currentData = timeframe === "5Y" ? data5Years : data1Year;

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 mt-6 transition-colors duration-200">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-lg font-bold text-slate-800 dark:text-white">
            Tax Alpha Generation
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Portfolio value: Standard vs. Harvested over time
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

      <div className="h-[300px] w-full mt-4">
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
              dataKey="year"
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
              tickFormatter={(value) => `₹${value / 1000}k`}
            />
            <Tooltip
              contentStyle={{
                borderRadius: "8px",
                border: "none",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
              }}
            />
            <Area
              type="monotone"
              dataKey="Standard"
              stroke="#94a3b8"
              fillOpacity={1}
              fill="url(#colorStandard)"
            />
            <Area
              type="monotone"
              dataKey="Harvested"
              stroke="#10b981"
              fillOpacity={1}
              fill="url(#colorHarvested)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
