import Link from "next/link";
import { Settings } from "lucide-react";
import TradeTable from "@/components/TradeTable";
import StatCard from "@/components/StatCard";
import TaxAlphaChart from "@/components/TaxAlphaChart";
import { IndianRupee, TrendingUp, BarChart3 } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-slate-900">
            Tax-Loss Harvesting Dashboard
          </h1>
          <Link
            href="/settings"
            className="p-2 bg-white rounded-lg border border-slate-200 text-slate-500 hover:text-blue-600 hover:border-blue-200 transition-colors shadow-sm"
          >
            <Settings className="w-5 h-5" />
          </Link>
        </div>

        {/* This is a CSS Grid - it puts the cards in a row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatCard
            title="Total Tax Saved"
            value="₹45,200"
            icon={IndianRupee}
            trend="+12%"
            trendType="positive"
          />
          <StatCard
            title="Harvesting Alpha"
            value="3.2%"
            icon={TrendingUp}
            trend="+0.5%"
            trendType="positive"
          />
          <StatCard
            title="Active Opportunities"
            value="12 Stocks"
            icon={BarChart3}
            trend="-2"
            trendType="negative"
          />
        </div>
        <TaxAlphaChart />
        <TradeTable />
      </div>
    </main>
  );
}
