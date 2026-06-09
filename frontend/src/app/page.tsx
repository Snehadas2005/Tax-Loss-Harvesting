"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import StatCard from "@/components/StatCard";
import { Settings } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

const TaxAlphaChart = dynamic(() => import("@/components/TaxAlphaChart"), { ssr: false });
const TradeTable = dynamic(() => import("@/components/TradeTable"), { ssr: false });
const OpportunitiesPanel = dynamic(() => import("@/components/OpportunitiesPanel"), { ssr: false });

interface StatData {
  title: string;
  value: string;
  trend: string;
}

export default function Home() {
  const [stats, setStats] = useState<StatData[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .dashboard()
      .then((data) => {
        setStats(data.stats || []);
      })
      .catch((err) => {
        console.error("Failed to fetch dashboard summary", err);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  return (
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
          {isLoading ? (
            <>
              <div className="h-28 bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 animate-pulse" />
              <div className="h-28 bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 animate-pulse" />
              <div className="h-28 bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 animate-pulse" />
            </>
          ) : (
            stats.map((stat: StatData, index: number) => (
              <StatCard
                key={stat.title}
                title={stat.title}
                value={stat.value}
                trend={stat.trend}
                icon={index === 0 ? "currency" : index === 1 ? "chart" : "list"}
              />
            ))
          )}
        </div>

        <TaxAlphaChart />
        <OpportunitiesPanel />
        <TradeTable />
      </div>
    </main>
  );
}
