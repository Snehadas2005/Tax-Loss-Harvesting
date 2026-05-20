"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Mail, ArrowRight, TrendingUp, AlertCircle } from "lucide-react";

// Here is your Mock Database of valid users!
const VALID_ACCOUNTS = [
  { email: "admin@test.com", password: "password123" },
  { email: "ansh@test.com", password: "frontend123" },
  { email: "team@test.com", password: "demo123" },
];

export default function LoginPage() {
  const router = useRouter();

  // Added state to track inputs and errors
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(""); // Clear any previous errors

    // Check if the typed credentials match ANY of our 3 valid accounts
    const isValid = VALID_ACCOUNTS.some(
      (account) => account.email === email && account.password === password,
    );

    // Simulate the time it takes to talk to a real server
    setTimeout(() => {
      setIsLoading(false);

      if (isValid) {
        // Success! Send to dashboard
        router.push("/");
      } else {
        // Failure! Trigger the error UI
        setError("Invalid email or password. Please try again.");
      }
    }, 800);
  };

  return (
    <main className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col items-center justify-center p-4 transition-colors duration-200">
      <div className="mb-8 flex flex-col items-center">
        <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mb-4 shadow-lg shadow-blue-500/30">
          <TrendingUp className="w-6 h-6 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Tax-Loss Harvester
        </h1>
        <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
          Sign in to your portfolio dashboard
        </p>
      </div>

      <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-100 dark:border-slate-800 p-8 transition-colors duration-200">
        {/* NEW: The Error Banner UI */}
        {error && (
          <div className="mb-6 p-3 bg-rose-50 dark:bg-rose-900/30 border border-rose-200 dark:border-rose-800/50 rounded-lg flex items-start gap-2 animate-in fade-in slide-in-from-top-2 duration-200">
            <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
            <p className="text-sm text-rose-600 dark:text-rose-400 font-medium">
              {error}
            </p>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white transition-all"
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                Password
              </label>
              <a
                href="#"
                className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
              >
                Forgot password?
              </a>
            </div>
            <div className="relative">
              <Lock className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 mt-4 disabled:opacity-70"
          >
            {isLoading ? (
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            ) : (
              <>
                Sign In
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>
      </div>
    </main>
  );
}
