import { LucideIcon } from "lucide-react";

// This is a "Type Definition" - it tells TypeScript exactly what
// information this component needs to work.
interface StatCardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  trend: string;
  trendType: "positive" | "negative";
}

export default function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  trendType,
}: StatCardProps) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex flex-col gap-4">
      <div className="flex justify-between items-center">
        {/* The Title */}
        <span className="text-slate-500 text-sm font-medium">{title}</span>
        {/* The Icon Container */}
        <div className="bg-blue-50 p-2 rounded-lg">
          <Icon className="w-5 h-5 text-blue-600" />
        </div>
      </div>
      <div>
        {/* The Main Number */}
        <h3 className="text-2xl font-bold text-slate-900">{value}</h3>
        {/* The Trend Text (Changes color based on trendType) */}
        <p
          className={`text-xs mt-1 font-medium ${trendType === "positive" ? "text-emerald-600" : "text-rose-600"}`}
        >
          {trend}{" "}
          <span className="text-slate-400 font-normal">vs last month</span>
        </p>
      </div>
    </div>
  );
}
