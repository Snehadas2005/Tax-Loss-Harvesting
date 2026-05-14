"use client";

import { useState, useEffect } from "react";
// Added the 'X' icon for our close button, and 'Info' for the modal
import {
  ArrowRight,
  CheckCircle2,
  Search,
  Loader2,
  X,
  Info,
} from "lucide-react";

// I added 'reason' and 'fees' to the mock data to make the modal interesting!
const mockDatabase = [
  {
    id: 1,
    date: "Nov 15, 2023",
    sold: "INFY.NS",
    bought: "TCS.NS",
    taxSaved: 4500,
    status: "Completed",
    reason:
      "INFY dropped 8% below cost basis. Swapped to TCS to maintain IT sector exposure.",
    fees: 15.5,
  },
  {
    id: 2,
    date: "Oct 02, 2023",
    sold: "HDFCBANK.NS",
    bought: "ICICIBANK.NS",
    taxSaved: 12000,
    status: "Completed",
    reason:
      "HDFCBANK stagnant. Harvested loss to offset previous capital gains.",
    fees: 22.0,
  },
  {
    id: 3,
    date: "Aug 21, 2023",
    sold: "RELIANCE.NS",
    bought: "ONGC.NS",
    taxSaved: 8500,
    status: "Completed",
    reason: "Energy sector rebalancing. Captured 5% loss on RELIANCE.",
    fees: 18.75,
  },
  {
    id: 4,
    date: "Jul 10, 2023",
    sold: "WIPRO.NS",
    bought: "HCLTECH.NS",
    taxSaved: 3200,
    status: "Completed",
    reason: "Algorithmic trigger: 30-day moving average crossover.",
    fees: 12.0,
  },
  {
    id: 5,
    date: "Jun 05, 2023",
    sold: "TCS.NS",
    bought: "WIPRO.NS",
    taxSaved: 2100,
    status: "Pending",
    reason: "Awaiting market open for execution.",
    fees: 0.0,
  },
];

type Trade = (typeof mockDatabase)[0];

export default function TradeTable() {
  const [searchTerm, setSearchTerm] = useState("");
  const [trades, setTrades] = useState<Trade[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // NEW STATE: This remembers which trade was clicked. Null means no trade is clicked.
  const [selectedTrade, setSelectedTrade] = useState<Trade | null>(null);

  useEffect(() => {
    const fetchFakeData = setTimeout(() => {
      setTrades(mockDatabase);
      setIsLoading(false);
    }, 1500);
    return () => clearTimeout(fetchFakeData);
  }, []);

  const filteredTrades = trades.filter((trade) => {
    const searchLower = searchTerm.toLowerCase();
    return (
      trade.sold.toLowerCase().includes(searchLower) ||
      trade.bought.toLowerCase().includes(searchLower)
    );
  });

  return (
    // We added 'relative' here so the modal knows where to attach itself
    <div className="relative bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden mt-6 mb-12">
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
            {isLoading ? (
              <tr>
                <td colSpan={4} className="p-12 text-center text-slate-500">
                  <div className="flex flex-col items-center justify-center gap-2">
                    <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
                    <p>Fetching data from simulation engine...</p>
                  </div>
                </td>
              </tr>
            ) : filteredTrades.length > 0 ? (
              filteredTrades.map((trade) => (
                <tr
                  key={trade.id}
                  // NEW: When a row is clicked, save that specific trade into our state!
                  onClick={() => setSelectedTrade(trade)}
                  // NEW: Added cursor-pointer so the mouse turns into a hand
                  className="border-b border-slate-50 hover:bg-slate-50 transition-colors cursor-pointer"
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

      {/* --- NEW: THE MODAL POPUP --- */}
      {/* If selectedTrade is NOT null, draw this HTML on top of everything */}
      {selectedTrade && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm">
          {/* The Modal Card */}
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="bg-slate-50 p-4 border-b border-slate-100 flex items-center justify-between">
              <h4 className="font-bold text-slate-800 flex items-center gap-2">
                <Info className="w-5 h-5 text-blue-500" />
                Execution Details
              </h4>
              {/* Close Button: Sets state back to null! */}
              <button
                onClick={() => setSelectedTrade(null)}
                className="p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-200 rounded-md transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="text-sm text-slate-500">Transaction Date</span>
                <span className="font-medium text-slate-800">
                  {selectedTrade.date}
                </span>
              </div>

              <div>
                <p className="text-sm text-slate-500 mb-1">
                  Algorithm Reasoning
                </p>
                <p className="text-sm text-slate-700 bg-blue-50 p-3 rounded-lg border border-blue-100 leading-relaxed">
                  {selectedTrade.reason}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-100">
                  <p className="text-xs text-emerald-600 mb-1 font-medium">
                    Net Tax Saved
                  </p>
                  <p className="text-lg font-bold text-emerald-700">
                    ₹{selectedTrade.taxSaved.toLocaleString()}
                  </p>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-xs text-slate-500 mb-1 font-medium">
                    Brokerage Fees
                  </p>
                  <p className="text-lg font-bold text-slate-700">
                    ₹{selectedTrade.fees.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-end">
              <button
                onClick={() => setSelectedTrade(null)}
                className="px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-lg text-sm font-medium hover:bg-slate-100 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
