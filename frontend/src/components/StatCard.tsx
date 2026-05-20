import { IndianRupee, TrendingUp, ListChecks } from "lucide-react";

// Notice how we are teaching it what 'icon' means right here!
interface StatCardProps {
  title: string;
  value: string;
  trend: string;
  icon: "currency" | "chart" | "list";
}

export default function StatCard({ title, value, trend, icon }: StatCardProps) {
  const isPositive = trend.startsWith("+");

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 transition-colors duration-200">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400">
          {title}
        </h3>
        <div className="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
          {icon === "currency" && (
            <IndianRupee className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          )}
          {icon === "chart" && (
            <TrendingUp className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          )}
          {icon === "list" && (
            <ListChecks className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          )}
        </div>
      </div>
      <div className="flex items-baseline gap-2">
        <h2 className="text-2xl font-bold text-slate-800 dark:text-white">
          {value}
        </h2>
        <span
          className={`text-xs font-medium ${isPositive ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}
        >
          {trend}
        </span>
      </div>
      <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">
        vs last month
      </p>
    </div>
  );
}
