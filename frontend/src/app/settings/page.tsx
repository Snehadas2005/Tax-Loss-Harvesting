"use client";

import { Moon, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react"; // 1. Import useEffect and useState

export default function SettingsPage() {
  // 2. Grab 'resolvedTheme' instead of just 'theme'
  const { setTheme, resolvedTheme } = useTheme();

  // 3. Create a 'mounted' state to prevent React confusion
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-950 p-8 transition-colors duration-200">
      <div className="max-w-3xl mx-auto">
        <Link
          href="/"
          className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400 mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Dashboard
        </Link>

        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-8">
          Account Settings
        </h1>

        <div className="bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 p-6 transition-colors duration-200">
          <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
            <Moon className="w-5 h-5 text-slate-400 dark:text-blue-400" />{" "}
            Appearance
          </h3>

          <div className="flex items-center justify-between py-3">
            <div>
              <p className="font-medium text-slate-700 dark:text-slate-200">
                Dark Mode
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Toggle dark mode interface.
              </p>
            </div>

            {/* 4. Only draw the button AFTER the page mounts and knows the true theme */}
            {mounted ? (
              <button
                onClick={() =>
                  setTheme(resolvedTheme === "dark" ? "light" : "dark")
                }
                className={`w-11 h-6 rounded-full relative transition-colors duration-300 focus:outline-none ${resolvedTheme === "dark" ? "bg-blue-600" : "bg-slate-300"}`}
              >
                <div
                  className={`w-4 h-4 bg-white rounded-full absolute top-1 transition-transform duration-300 ${resolvedTheme === "dark" ? "translate-x-6" : "translate-x-1"}`}
                ></div>
              </button>
            ) : (
              // A temporary invisible placeholder so the layout doesn't jump
              <div className="w-11 h-6"></div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
