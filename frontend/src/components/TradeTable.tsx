"use client";

import { useState, useEffect } from "react"; // 1. Import useEffect!
import { ArrowRight, CheckCircle2, Search, Loader2 } from "lucide-react";

// We keep the mock data here, but imagine this is sitting on Adveta's database
const mockDatabase = [
  {
    id: 1,
    date: "Nov 15, 2023",
    sold: "INFY.NS",
    bought: "TCS.NS",
    taxSaved: 4500,
    status: "Completed",
  },
  {
    id: 2,
    date: "Oct 02, 2023",
    sold: "HDFCBANK.NS",
    bought: "ICICIBANK.NS",
    taxSaved: 12000,
    status: "Completed",
  },
  {
    id: 3,
    date: "Aug 21, 2023",
    sold: "RELIANCE.NS",
    bought: "ONGC.NS",
    taxSaved: 8500,
    status: "Completed",
  },
  {
    id: 4,
    date: "Jul 10, 2023",
    sold: "WIPRO.NS",
    bought: "HCLTECH.NS",
    taxSaved: 3200,
    status: "Completed",
  },
  {
    id: 5,
    date: "Jun 05, 2023",
    sold: "TCS.NS",
    bought: "WIPRO.NS",
    taxSaved: 2100,
    status: "Pending",
  },
];

// Define a Type for our Data so TypeScript stays happy
type Trade = (typeof mockDatabase)[0];

export default function TradeTable() {
  const [searchTerm, setSearchTerm] = useState("");

  // 2. New States for Data Fetching
  const [trades, setTrades] = useState<Trade[]>([]); // Starts as an empty array
  const [isLoading, setIsLoading] = useState(true); // Starts as 'true' because we are loading!

  // 3. The useEffect API Handshake
  useEffect(() => {
    // This code runs EXACTLY ONCE when the component first appears on screen

    // We use setTimeout to fake a slow internet connection / server response
    const fetchFakeData = setTimeout(() => {
      setTrades(mockDatabase); // Put the data into state
      setIsLoading(false); // Turn off the loading spinner
    }, 1500); // 1500 milliseconds = 1.5 seconds

    // Cleanup function
    return () => clearTimeout(fetchFakeData);
  }, []); // <-- This empty array [] means "Only run this once on load"

  // 4. Filtering Logic (now uses the 'trades' state instead of the hardcoded array)
  const filteredTrades = trades.filter((trade) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      trade.sold.toLowerCase().includes(searchLower) ||
      trade.bought.toLowerCase().includes(searchLower)
    );
  });

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden mt-6 mb-12">
      <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800">
            Recent Harvesting Events
          </h3>
          <p className="text-sm text-slate-500">
            A log of all tax-loss swaps executed by the algorithm.
          </p>
        </div>
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search stock ticker..."
            onChange={(e) => setSearchTerm(e.target.value)}
            value={searchTerm}
            className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-64"
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 text-slate-500 text-sm border-b border-slate-100">
              <th className="p-4 font-medium">Date</th>
              <th className="p-4 font-medium">Action (Sold → Bought)</th>
              <th className="p-4 font-medium">Tax Saved</th>
              <th className="p-4 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="text-sm">
            {/* 5. Handle the Loading UI */}
            {isLoading ? (
              <tr>
                <td colSpan={4} className="p-12 text-center text-slate-500">
                  <div className="flex flex-col items-center justify-center gap-2">
                    {/* A spinning loading icon */}
                    <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
                    <p>Fetching data from simulation engine...</p>
                  </div>
                </td>
              </tr>
            ) : filteredTrades.length > 0 ? (
              filteredTrades.map((trade) => (
                <tr
                  key={trade.id}
                  className="border-b border-slate-50 hover:bg-slate-50 transition-colors"
                >
                  <td className="p-4 text-slate-600">{trade.date}</td>
                  <td className="p-4 flex items-center gap-3 font-medium">
                    <span className="text-rose-600 bg-rose-50 px-2 py-1 rounded border border-rose-100">
                      {trade.sold}
                    </span>
                    <ArrowRight className="w-4 h-4 text-slate-400" />
                    <span className="text-emerald-600 bg-emerald-50 px-2 py-1 rounded border border-emerald-100">
                      {trade.bought}
                    </span>
                  </td>
                  <td className="p-4 font-bold text-slate-700">
                    ₹{trade.taxSaved.toLocaleString()}
                  </td>
                  <td className="p-4">
                    <span
                      className={`flex items-center gap-1.5 w-fit px-2.5 py-1 rounded-full text-xs font-medium ${
                        trade.status === "Completed"
                          ? "text-emerald-600 bg-emerald-50"
                          : "text-amber-600 bg-amber-50"
                      }`}
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      {trade.status}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="p-8 text-center text-slate-500">
                  No trades found matching "{searchTerm}"
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
