"use client";

import { useState } from "react";
import { api } from "@/lib/api";

const METHOD_PARAMS: Record<string, string[]> = {
  fixed: ["size"],
  percent_risk: ["account_size", "risk_pct", "entry_price", "stop_price"],
  kelly: ["win_rate", "avg_win", "avg_loss"],
  volatility: ["account_size", "target_risk", "price", "atr"],
};

export default function RiskPage() {
  const [method, setMethod] = useState("percent_risk");
  const [params, setParams] = useState<Record<string, string>>({});
  const [sizeResult, setSizeResult] = useState<Record<string, unknown> | null>(null);

  const [riskSymbols, setRiskSymbols] = useState("AAPL, GOOGL, MSFT");
  const [riskWeights, setRiskWeights] = useState("0.4, 0.3, 0.3");
  const [riskStart, setRiskStart] = useState("2023-01-01");
  const [riskEnd, setRiskEnd] = useState("2024-12-31");
  const [riskResult, setRiskResult] = useState<Record<string, unknown> | null>(null);
  const [riskError, setRiskError] = useState("");

  const calcPositionSize = async () => {
    const numParams: Record<string, number> = {};
    for (const [k, v] of Object.entries(params)) {
      numParams[k] = Number(v);
    }
    try {
      const res = await api.post<Record<string, unknown>>("/api/risk/position-size", {
        method,
        params: numParams,
      });
      setSizeResult(res);
    } catch {
      setSizeResult({ error: "Calculation failed" });
    }
  };

  const calcPortfolioRisk = async () => {
    const symbols = riskSymbols.split(",").map((s) => s.trim()).filter(Boolean);
    const weights = riskWeights.split(",").map((s) => Number(s.trim())).filter((n) => !isNaN(n));
    if (symbols.length === 0) {
      setRiskError("Enter at least one symbol");
      return;
    }
    setRiskError("");
    try {
      const res = await api.post<Record<string, unknown>>("/api/risk/portfolio", {
        symbols,
        weights,
        start: riskStart,
        end: riskEnd,
      });
      setRiskResult(res);
    } catch {
      setRiskResult({ error: "Risk calculation failed" });
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Risk & Position Sizing</h1>

      {/* Position Sizing */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">Position Sizing</h2>
        <div className="mb-3">
          <label className="block text-sm font-medium mb-1">Method</label>
          <select
            value={method}
            onChange={(e) => { setMethod(e.target.value); setParams({}); setSizeResult(null); }}
            className="border rounded px-3 py-2 w-full md:w-64"
          >
            {Object.keys(METHOD_PARAMS).map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {(METHOD_PARAMS[method] || []).map((field) => (
            <div key={field}>
              <label className="block text-sm text-gray-600 mb-1">{field}</label>
              <input
                type="number"
                className="border rounded px-3 py-2 w-full"
                value={params[field] || ""}
                onChange={(e) => setParams({ ...params, [field]: e.target.value })}
                step="any"
              />
            </div>
          ))}
        </div>
        <button
          onClick={calcPositionSize}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Calculate
        </button>
        {sizeResult && (
          <div className="mt-4 p-3 bg-gray-50 rounded">
            <h3 className="text-sm font-medium mb-2">Result</h3>
            <pre className="text-sm overflow-auto">{JSON.stringify(sizeResult, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* Portfolio Risk */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-3">Portfolio Risk Metrics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Symbols</label>
            <input
              className="border rounded px-3 py-2 w-full"
              value={riskSymbols}
              onChange={(e) => setRiskSymbols(e.target.value)}
              placeholder="AAPL, GOOGL, MSFT"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Weights</label>
            <input
              className="border rounded px-3 py-2 w-full"
              value={riskWeights}
              onChange={(e) => setRiskWeights(e.target.value)}
              placeholder="0.4, 0.3, 0.3"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Start</label>
            <input type="date" className="border rounded px-3 py-2 w-full" value={riskStart} onChange={(e) => setRiskStart(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">End</label>
            <input type="date" className="border rounded px-3 py-2 w-full" value={riskEnd} onChange={(e) => setRiskEnd(e.target.value)} />
          </div>
        </div>
        {riskError && <p className="text-red-600 text-sm mb-2">{riskError}</p>}
        <button
          onClick={calcPortfolioRisk}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Compute Risk
        </button>
        {riskResult && (
          <div className="mt-4">
            <h3 className="text-sm font-medium mb-2">Risk Metrics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {Object.entries(riskResult).map(([key, val]) => (
                <div key={key} className="bg-gray-50 rounded p-3">
                  <div className="text-xs text-gray-500">{key}</div>
                  <div className="text-lg font-semibold">
                    {typeof val === "number" ? val.toFixed(4) : String(val)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
