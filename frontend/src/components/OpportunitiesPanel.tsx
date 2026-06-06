"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import {
  TrendingDown,
  Sparkles,
  HelpCircle,
  Plus,
  Trash2,
  Loader2,
  RefreshCw,
  CheckCircle,
  AlertCircle
} from "lucide-react";

export default function OpportunitiesPanel() {
  const [portfolio, setPortfolio] = useState([
    { ticker: "AAPL", purchasePrice: 190.0, currentPrice: 161.5 },
    { ticker: "MSFT", purchasePrice: 420.0, currentPrice: 425.0 },
    { ticker: "TSLA", purchasePrice: 240.0, currentPrice: 180.0 },
    { ticker: "JPM", purchasePrice: 195.0, currentPrice: 170.0 }
  ]);

  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const [newTicker, setNewTicker] = useState("");
  const [newPurchasePrice, setNewPurchasePrice] = useState("");
  const [newCurrentPrice, setNewCurrentPrice] = useState("");

  const fetchRecommendations = () => {
    setIsLoading(true);
    // Transform parameters to match API structure
    const payload = portfolio.map(item => ({
      ticker: item.ticker.toUpperCase(),
      purchasePrice: Number(item.purchasePrice),
      currentPrice: Number(item.currentPrice)
    }));

    api.recommend(payload)
      .then((res) => {
        if (res && res.results) {
          setRecommendations(res.results);
        }
        setIsLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch ML recommendations", err);
        setIsLoading(false);
      });
  };

  useEffect(() => {
    fetchRecommendations();
  }, [portfolio]);

  const addAsset = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTicker || !newPurchasePrice || !newCurrentPrice) return;
    
    setPortfolio([
      ...portfolio,
      {
        ticker: newTicker.toUpperCase(),
        purchasePrice: Number(newPurchasePrice),
        currentPrice: Number(newCurrentPrice)
      }
    ]);
    setNewTicker("");
    setNewPurchasePrice("");
    setNewCurrentPrice("");
  };

  const removeAsset = (index: number) => {
    const updated = portfolio.filter((_, idx) => idx !== index);
    setPortfolio(updated);
  };

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 mt-6 transition-colors duration-200">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-emerald-500" />
            ML-Powered Harvesting Scanner
          </h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Configure your holdings below to scan for real-time tax-loss harvesting candidates and twin replacements.
          </p>
        </div>
        <button
          onClick={fetchRecommendations}
          disabled={isLoading}
          className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm font-medium transition-all disabled:opacity-50"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Re-scan
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Side: Holdings Editor */}
        <div className="lg:col-span-5 space-y-6">
          <div className="border border-slate-100 dark:border-slate-800 rounded-xl p-4 bg-slate-50/50 dark:bg-slate-800/20">
            <h4 className="font-bold text-sm text-slate-700 dark:text-slate-300 mb-3">Your Portfolio Holdings</h4>
            <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
              {portfolio.map((item, index) => (
                <div
                  key={index}
                  className="flex justify-between items-center p-2.5 bg-white dark:bg-slate-800 rounded-lg border border-slate-200/60 dark:border-slate-700/60 text-sm shadow-sm"
                >
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-800 dark:text-white">{item.ticker}</span>
                    <span className="text-xs text-slate-400 dark:text-slate-500">
                      Cost: ₹{item.purchasePrice} | Cur: ₹{item.currentPrice}
                    </span>
                  </div>
                  <button
                    onClick={() => removeAsset(index)}
                    className="p-1 hover:bg-rose-50 dark:hover:bg-rose-950/30 text-slate-400 hover:text-rose-500 rounded transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
              {portfolio.length === 0 && (
                <p className="text-xs text-slate-400 text-center py-4">No holdings. Add some assets below.</p>
              )}
            </div>
          </div>

          <form onSubmit={addAsset} className="space-y-3 p-4 border border-slate-100 dark:border-slate-800 rounded-xl">
            <h4 className="font-bold text-sm text-slate-700 dark:text-slate-300">Add Portfolio Asset</h4>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-[10px] uppercase font-bold text-slate-400 mb-1">Ticker</label>
                <input
                  type="text"
                  placeholder="e.g. TSLA"
                  value={newTicker}
                  onChange={(e) => setNewTicker(e.target.value)}
                  className="w-full px-2.5 py-1.5 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-[10px] uppercase font-bold text-slate-400 mb-1">Buy Price</label>
                <input
                  type="number"
                  placeholder="100"
                  value={newPurchasePrice}
                  onChange={(e) => setNewPurchasePrice(e.target.value)}
                  className="w-full px-2.5 py-1.5 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-[10px] uppercase font-bold text-slate-400 mb-1">Cur Price</label>
                <input
                  type="number"
                  placeholder="90"
                  value={newCurrentPrice}
                  onChange={(e) => setNewCurrentPrice(e.target.value)}
                  className="w-full px-2.5 py-1.5 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <button
              type="submit"
              className="w-full flex items-center justify-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold transition-colors"
            >
              <Plus className="w-4 h-4" /> Add Asset
            </button>
          </form>
        </div>

        {/* Right Side: Recommendation Results */}
        <div className="lg:col-span-7 space-y-4">
          <h4 className="font-bold text-sm text-slate-700 dark:text-slate-300">Live Scanned Opportunities</h4>
          
          <div className="space-y-3 min-h-[280px]">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center min-h-[250px] gap-2">
                <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                <p className="text-sm text-slate-500 dark:text-slate-400">Scanning holdings via ML Model Arena...</p>
              </div>
            ) : recommendations.length > 0 ? (
              recommendations.map((rec, index) => {
                const isHarvest = rec.recommended_action === "HARVEST_NOW";
                const isWarning = rec.recommended_action === "HOLD_REBOUND_LIKELY";
                
                return (
                  <div
                    key={index}
                    className={`p-4 rounded-xl border transition-all ${
                      isHarvest
                        ? "bg-rose-50/40 border-rose-200 dark:bg-rose-950/10 dark:border-rose-900/30"
                        : isWarning
                        ? "bg-amber-50/40 border-amber-200 dark:bg-amber-950/10 dark:border-amber-900/30"
                        : "bg-slate-50/40 border-slate-200/60 dark:bg-slate-800/10 dark:border-slate-800/30"
                    }`}
                  >
                    <div className="flex justify-between items-start flex-col sm:flex-row gap-3">
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-black text-slate-900 dark:text-white text-base">{rec.ticker}</span>
                          <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                            rec.current_loss_pct <= 0 
                              ? "text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/20"
                              : "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20"
                          }`}>
                            Loss: {rec.current_loss_pct}%
                          </span>
                          <span className="text-xs text-slate-400 dark:text-slate-500">
                            Forecast 30d Return: {rec.predicted_30d_return_pct}%
                          </span>
                        </div>
                        
                        {isHarvest && rec.suggested_substitutes && rec.suggested_substitutes.length > 0 && (
                          <div className="mt-2.5 flex items-center gap-2 flex-wrap">
                            <span className="text-xs font-medium text-slate-500">Risk Twin Replacements:</span>
                            {rec.suggested_substitutes.map((sub: string) => (
                              <span
                                key={sub}
                                className="text-xs font-bold px-2 py-0.5 bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 rounded border border-emerald-100 dark:border-emerald-800/30"
                              >
                                {sub}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      <span
                        className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
                          isHarvest
                            ? "text-rose-700 dark:text-rose-400 bg-rose-100 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/30"
                            : isWarning
                            ? "text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-900/30"
                            : "text-slate-600 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700"
                        }`}
                      >
                        {isHarvest ? (
                          <>
                            <TrendingDown className="w-3.5 h-3.5" />
                            HARVEST NOW
                          </>
                        ) : isWarning ? (
                          <>
                            <AlertCircle className="w-3.5 h-3.5" />
                            HOLD (REBOUND LIKELY)
                          </>
                        ) : (
                          <>
                            <CheckCircle className="w-3.5 h-3.5" />
                            HOLD (ASSET HEALTHY)
                          </>
                        )}
                      </span>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="flex flex-col items-center justify-center min-h-[280px] border border-dashed border-slate-200 dark:border-slate-800 rounded-xl">
                <HelpCircle className="w-8 h-8 text-slate-400 mb-2" />
                <p className="text-sm text-slate-500 dark:text-slate-400">Add assets to scan for opportunities.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
