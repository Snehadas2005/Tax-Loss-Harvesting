"use client";

import { useState } from "react"; // 1. Import the useState hook
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// Our 5-year data
const fiveYearData = [
  { year: "2019", Standard: 100000, Harvested: 100000 },
  { year: "2020", Standard: 108000, Harvested: 111500 },
  { year: "2021", Standard: 125000, Harvested: 132000 },
  { year: "2022", Standard: 115000, Harvested: 126000 },
  { year: "2023", Standard: 135000, Harvested: 149500 },
];

// Our 1-year data (just monthly data for 2023)
const oneYearData = [
  { year: "Jan", Standard: 126000, Harvested: 126000 },
  { year: "Apr", Standard: 128000, Harvested: 131000 },
  { year: "Jul", Standard: 131000, Harvested: 138000 },
  { year: "Oct", Standard: 129000, Harvested: 142000 },
  { year: "Dec", Standard: 135000, Harvested: 149500 },
];

export default function TaxAlphaChart() {
  // 2. Create the State.
  // 'timeframe' is the current value. 'setTimeframe' is the function to change it.
  const [timeframe, setTimeframe] = useState<"1Y" | "5Y">("5Y");

  // 3. Decide which data to show based on the state
  const currentData = timeframe === "5Y" ? fiveYearData : oneYearData;

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col gap-4 mt-6">
      <div className="flex justify-between items-start">
        <div className="flex flex-col">
          <h3 className="text-lg font-bold text-slate-800">
            Tax Alpha Generation
          </h3>
          <p className="text-sm text-slate-500">
            Portfolio value: Standard vs. Harvested over time
          </p>
        </div>

        <div className="flex bg-slate-100 p-1 rounded-lg">
          <button
            onClick={() => setTimeframe("1Y")}
            className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${timeframe === "1Y" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"}`}
          >
            1 Year
          </button>
          <button
            onClick={() => setTimeframe("5Y")}
            className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${timeframe === "5Y" ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700"}`}
          >
            5 Years
          </button>
        </div>
      </div>

      {/* The Chart */}
      <div className="h-[300px] w-full mt-4">
        <ResponsiveContainer width="100%" height="100%">
          {/* NO QUOTES around the curly braces here! */}
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

            {/* NO QUOTES around the contentStyle braces here either! */}
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
