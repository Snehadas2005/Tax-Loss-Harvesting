import StatCard from "@/components/StatCard";
import TaxAlphaChart from "@/components/TaxAlphaChart";
import TradeTable from "@/components/TradeTable";
import { Settings } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    // Added dark:bg-slate-950 here for the main background
    <main className="min-h-screen bg-slate-50 dark:bg-slate-950 p-8 transition-colors duration-200">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Tax-Loss Harvesting Dashboard
          </h1>
          <Link
            href="/settings"
            className="p-2 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:border-blue-200 transition-colors shadow-sm"
          >
            <Settings className="w-5 h-5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Total Tax Saved"
            value="₹45,200"
            trend="+12%"
            icon="currency"
          />
          <StatCard
            title="Harvesting Alpha"
            value="3.2%"
            trend="+0.5%"
            icon="chart"
          />
          <StatCard
            title="Active Opportunities"
            value="12 Stocks"
            trend="-2"
            icon="list"
          />
        </div>

        <TaxAlphaChart />
        <TradeTable />
      </div>
    </main>
  );
}
