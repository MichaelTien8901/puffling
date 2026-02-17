"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function PortfolioPage() {
  // Optimization
  const [optSymbols, setOptSymbols] = useState("AAPL, GOOGL, MSFT");
  const [optStart, setOptStart] = useState("2023-01-01");
  const [optEnd, setOptEnd] = useState("2024-12-31");
  const [optMethod, setOptMethod] = useState("mean_variance");
  const [optResult, setOptResult] = useState<Record<string, unknown> | null>(null);
  const [optError, setOptError] = useState("");

  // Tearsheet
  const [returns, setReturns] = useState("0.01, 0.02, -0.005, 0.03, -0.01");
  const [tearsheet, setTearsheet] = useState<Record<string, unknown> | null>(null);

  // Factors
  const [facSymbols, setFacSymbols] = useState("AAPL, GOOGL, MSFT");
  const [facStart, setFacStart] = useState("2023-01-01");
  const [facEnd, setFacEnd] = useState("2024-12-31");
  const [facResult, setFacResult] = useState<Record<string, unknown> | null>(null);
  const [pcaResult, setPcaResult] = useState<Record<string, unknown> | null>(null);
  const [nComponents, setNComponents] = useState(5);

  const runOptimize = async () => {
    setOptError("");
    try {
      const res = await api.post<Record<string, unknown>>("/api/portfolio/optimize", {
        symbols: optSymbols.split(",").map((s) => s.trim()).filter(Boolean),
        start: optStart,
        end: optEnd,
        method: optMethod,
      });
      setOptResult(res);
    } catch {
      setOptError("Optimization failed");
    }
  };

  const runTearsheet = async () => {
    try {
      const vals = returns.split(",").map((s) => Number(s.trim())).filter((n) => !isNaN(n));
      const res = await api.post<Record<string, unknown>>("/api/portfolio/tearsheet", { returns: vals });
      setTearsheet(res);
    } catch {
      setTearsheet({ error: "Tearsheet generation failed" });
    }
  };

  const runFactors = async () => {
    try {
      const res = await api.post<Record<string, unknown>>("/api/factors/compute", {
        symbols: facSymbols.split(",").map((s) => s.trim()).filter(Boolean),
        start: facStart,
        end: facEnd,
      });
      setFacResult(res);
    } catch {
      setFacResult({ error: "Factor computation failed" });
    }
  };

  const runPCA = async () => {
    try {
      const res = await api.post<Record<string, unknown>>("/api/factors/risk-factors", {
        symbols: facSymbols.split(",").map((s) => s.trim()).filter(Boolean),
        start: facStart,
        end: facEnd,
        n_components: nComponents,
      });
      setPcaResult(res);
    } catch {
      setPcaResult({ error: "PCA computation failed" });
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Portfolio</h1>

      {/* Portfolio Optimization */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">Portfolio Optimization</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Symbols</label>
            <input className="border rounded px-3 py-2 w-full" value={optSymbols} onChange={(e) => setOptSymbols(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Start</label>
            <input type="date" className="border rounded px-3 py-2 w-full" value={optStart} onChange={(e) => setOptStart(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">End</label>
            <input type="date" className="border rounded px-3 py-2 w-full" value={optEnd} onChange={(e) => setOptEnd(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Method</label>
            <select className="border rounded px-3 py-2 w-full" value={optMethod} onChange={(e) => setOptMethod(e.target.value)}>
              <option value="mean_variance">Mean-Variance</option>
              <option value="min_variance">Min Variance</option>
              <option value="max_sharpe">Max Sharpe</option>
            </select>
          </div>
        </div>
        {optError && <p className="text-red-600 text-sm mb-2">{optError}</p>}
        <button onClick={runOptimize} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Optimize</button>
        {optResult && (
          <div className="mt-4">
            <h3 className="text-sm font-medium mb-2">Optimal Weights</h3>
            {optResult.weights && typeof optResult.weights === "object" ? (
              <table className="w-full text-sm">
                <thead><tr className="text-left text-gray-500 border-b"><th className="py-1">Symbol</th><th className="py-1">Weight</th></tr></thead>
                <tbody>
                  {Object.entries(optResult.weights as Record<string, number>).map(([sym, w]) => (
                    <tr key={sym} className="border-t"><td className="py-1">{sym}</td><td className="py-1">{Number(w).toFixed(4)}</td></tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <pre className="text-sm bg-gray-50 p-3 rounded overflow-auto">{JSON.stringify(optResult, null, 2)}</pre>
            )}
          </div>
        )}
      </div>

      {/* Tearsheet */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">Performance Tearsheet</h2>
        <div className="mb-4">
          <label className="block text-sm text-gray-600 mb-1">Returns (comma-separated)</label>
          <input className="border rounded px-3 py-2 w-full" value={returns} onChange={(e) => setReturns(e.target.value)} placeholder="0.01, 0.02, -0.005" />
        </div>
        <button onClick={runTearsheet} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Generate Tearsheet</button>
        {tearsheet && (
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(tearsheet).map(([key, val]) => (
              <div key={key} className="bg-gray-50 rounded p-3">
                <div className="text-xs text-gray-500">{key}</div>
                <div className="text-lg font-semibold">{typeof val === "number" ? val.toFixed(4) : String(val)}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Factor Analysis */}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-3">Factor Analysis</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Symbols</label>
            <input className="border rounded px-3 py-2 w-full" value={facSymbols} onChange={(e) => setFacSymbols(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Start</label>
            <input type="date" className="border rounded px-3 py-2 w-full" value={facStart} onChange={(e) => setFacStart(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">End</label>
            <input type="date" className="border rounded px-3 py-2 w-full" value={facEnd} onChange={(e) => setFacEnd(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">PCA Components</label>
            <input type="number" className="border rounded px-3 py-2 w-full" value={nComponents} onChange={(e) => setNComponents(Number(e.target.value))} min={1} max={20} />
          </div>
        </div>
        <div className="flex gap-3">
          <button onClick={runFactors} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Compute Factors</button>
          <button onClick={runPCA} className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700">Risk Factors (PCA)</button>
        </div>
        {facResult && (
          <div className="mt-4">
            <h3 className="text-sm font-medium mb-2">Factor Values</h3>
            <pre className="text-sm bg-gray-50 p-3 rounded overflow-auto">{JSON.stringify(facResult, null, 2)}</pre>
          </div>
        )}
        {pcaResult && (
          <div className="mt-4">
            <h3 className="text-sm font-medium mb-2">PCA Risk Factors</h3>
            <pre className="text-sm bg-gray-50 p-3 rounded overflow-auto">{JSON.stringify(pcaResult, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
