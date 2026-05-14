"use client"; // Required for interactivity (useState)

import { useState } from "react";
import { ArrowRight, CheckCircle2, Search } from "lucide-react";

// Our mock data
const tradeHistory = [
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

export default function TradeTable() {
  // 1. Create the State to hold whatever the user types
  const [searchTerm, setSearchTerm] = useState("");

  // 2. The Filtering Logic
  // We take the original array and filter it BEFORE drawing the table
  const filteredTrades = tradeHistory.filter((trade) => {
    // Convert everything to lowercase so "TCS" and "tcs" match
    const searchLower = searchTerm.toLowerCase();

    // Return true if the search term is found in the 'sold' OR 'bought' column
    return (
      trade.sold.toLowerCase().includes(searchLower) ||
      trade.bought.toLowerCase().includes(searchLower)
    );
  });

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden mt-6 mb-12">
      {/* Header & Search Bar Section */}
      <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-slate-800">
            Recent Harvesting Events
          </h3>
          <p className="text-sm text-slate-500">
            A log of all tax-loss swaps executed by the algorithm.
          </p>
        </div>

        {/* The Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search stock ticker..."
            // 3. When the user types, update the state!
            onChange={(e) => setSearchTerm(e.target.value)}
            value={searchTerm}
            className="pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full sm:w-64"
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
            {/* 4. Map through the FILTERED list, not the original list */}
            {filteredTrades.length > 0 ? (
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
              // 5. What to show if the search finds nothing
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
