import TradeTable from "@/components/TradeTable";
import StatCard from "@/components/StatCard";
import TaxAlphaChart from "@/components/TaxAlphaChart";
import { IndianRupee, TrendingUp, BarChart3 } from "lucide-react";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-2xl font-bold text-slate-900 mb-8">
          Tax-Loss Harvesting Dashboard
        </h1>

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
