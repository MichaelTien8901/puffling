"use client";

import { useState, useEffect, useRef } from "react";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/useToast";

export default function BacktestPage() {
  const [strategyType, setStrategyType] = useState("momentum");
  const [symbols, setSymbols] = useState("SPY");
  const [start, setStart] = useState("2024-01-01");
  const [end, setEnd] = useState("2024-12-31");
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [wsProgress, setWsProgress] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    return () => { wsRef.current?.close(); };
  }, []);

  const connectProgress = (backtestId: number) => {
    const baseUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    try {
      const ws = new WebSocket(`${baseUrl}/ws/backtest/${backtestId}`);
      wsRef.current = ws;
      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.progress) setWsProgress(`${Math.round(data.progress * 100)}%`);
          else if (data.status) setWsProgress(data.status);
        } catch {}
      };
      ws.onerror = () => setWsProgress("Running...");
      ws.onclose = () => {};
    } catch {
      setWsProgress("Running...");
    }
  };

  const runBacktest = async () => {
    setLoading(true);
    setResults(null);
    setWsProgress("Running...");
    try {
      const res = await api.post<Record<string, unknown>>("/api/backtest/", {
        strategy_type: strategyType,
        symbols: symbols.split(",").map((s) => s.trim()),
        start,
        end,
      });
      if (res.id) connectProgress(Number(res.id));
      setResults(res);
      setWsProgress(null);
    } catch {
      toast.error("Backtest failed");
      setWsProgress(null);
    }
    wsRef.current?.close();
    setLoading(false);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Backtest</h1>
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Strategy</label>
            <input className="border rounded px-3 py-2 w-full" value={strategyType} onChange={(e) => setStrategyType(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Symbols</label>
            <input className="border rounded px-3 py-2 w-full" value={symbols} onChange={(e) => setSymbols(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Start</label>
            <input type="date" className="border rounded px-3 py-2 w-full" value={start} onChange={(e) => setStart(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">End</label>
            <input type="date" className="border rounded px-3 py-2 w-full" value={end} onChange={(e) => setEnd(e.target.value)} />
          </div>
        </div>
        <button onClick={runBacktest} disabled={loading} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Running..." : "Run Backtest"}
        </button>
        {loading && wsProgress && (
          <div className="mt-3">
            <div className="flex items-center gap-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: wsProgress.includes("%") ? wsProgress : "100%" }} />
              </div>
              <span className="text-sm text-gray-600 whitespace-nowrap">{wsProgress}</span>
            </div>
          </div>
        )}
      </div>
      {results && (
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">Results</h2>
          <pre className="text-sm bg-gray-50 p-3 rounded overflow-auto">{JSON.stringify(results.metrics, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
