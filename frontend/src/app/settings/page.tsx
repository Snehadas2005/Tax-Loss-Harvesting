import { User, Bell, Shield, ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function SettingsPage() {
  return (
    <main className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-3xl mx-auto">
        {/* 1. The Next.js Link Component */}
        <Link
          href="/"
          className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-blue-600 mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Link>

        <h1 className="text-2xl font-bold text-slate-900 mb-8">
          Account Settings
        </h1>

        {/* Profile Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="bg-blue-100 p-4 rounded-full">
              <User className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-800">Ansh Jaiswal</h2>
              <p className="text-sm text-slate-500">Frontend Developer</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                value="ansh.jaiswal@example.com"
                disabled
                className="w-full p-2.5 border border-slate-200 rounded-lg bg-slate-50 text-slate-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Role
              </label>
              <input
                type="text"
                value="Lead Frontend Engineer"
                disabled
                className="w-full p-2.5 border border-slate-200 rounded-lg bg-slate-50 text-slate-500"
              />
            </div>
          </div>
        </div>

        {/* Preferences Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
          <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Bell className="w-5 h-5 text-slate-400" /> Notifications
          </h3>
          <div className="flex items-center justify-between py-3 border-b border-slate-50">
            <div>
              <p className="font-medium text-slate-700">Harvesting Alerts</p>
              <p className="text-sm text-slate-500">
                Email me when a tax-loss opportunity is found.
              </p>
            </div>
            {/* A simple mock toggle switch */}
            <div className="w-11 h-6 bg-blue-600 rounded-full relative cursor-pointer">
              <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1"></div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
