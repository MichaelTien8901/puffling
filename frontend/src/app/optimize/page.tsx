"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useWebSocket } from "@/hooks/useWebSocket";
import { useToast } from "@/hooks/useToast";

const DEFAULT_GRIDS: Record<string, Record<string, (number | string)[]>> = {
  momentum: {
    short_window: [5, 10, 20],
    long_window: [20, 50, 100],
    ma_type: ["sma", "ema"],
  },
  mean_reversion: {
    window: [10, 20, 30],
    num_std: [1.5, 2.0, 2.5],
    zscore_entry: [-2.5, -2.0, -1.5],
  },
  stat_arb: {
    lookback: [30, 60, 90],
    entry_zscore: [1.5, 2.0, 2.5],
    exit_zscore: [0.0, 0.5, 1.0],
  },
  market_making: {
    spread_bps: [5, 10, 20],
    max_inventory: [50, 100, 200],
  },
};

interface OptResult {
  rank: number;
  params: Record<string, unknown>;
  mean_sharpe: number;
  mean_return: number;
  max_drawdown: number;
  mean_win_rate: number;
  strategy_type?: string;
  recommended?: boolean;
}

interface SweepResults {
  by_strategy: Record<string, OptResult[]>;
  recommendation: {
    strategy_type: string | null;
    best_params: Record<string, unknown>;
    mean_sharpe: number;
    sharpe_std: number;
    confidence: string;
    recommended: boolean;
  } | null;
}

interface JobSummary {
  id: number;
  job_type: string;
  strategy_type: string;
  status: string;
  created_at: string;
  best_sharpe: number | null;
}

type SortKey = "rank" | "mean_sharpe" | "mean_return" | "max_drawdown" | "mean_win_rate";

export default function OptimizePage() {
  const [strategyType, setStrategyType] = useState("momentum");
  const [symbols, setSymbols] = useState("SPY");
  const [start, setStart] = useState("2020-01-01");
  const [end, setEnd] = useState("2024-12-31");
  const [nSplits, setNSplits] = useState(5);
  const [trainRatio, setTrainRatio] = useState(0.7);
  const [paramGrid, setParamGrid] = useState<Record<string, string>>({});
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState<{ combo: number; total: number } | null>(null);
  const [results, setResults] = useState<OptResult[]>([]);
  const [sortKey, setSortKey] = useState<SortKey>("rank");
  const [sortAsc, setSortAsc] = useState(true);

  const [sweepResults, setSweepResults] = useState<SweepResults | null>(null);
  const [expandedStrategy, setExpandedStrategy] = useState<string | null>(null);
  const [sweepProgress, setSweepProgress] = useState<{
    current_strategy: string;
    strategy_index: number;
    total_strategies: number;
    combo: number;
    total: number;
  } | null>(null);

  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);

  // Live Adaptation
  const [showAdaptation, setShowAdaptation] = useState(false);
  const [adaptations, setAdaptations] = useState<Record<string, unknown>[]>([]);
  const [adaptStrategy, setAdaptStrategy] = useState("momentum");
  const [expandedAdaptId, setExpandedAdaptId] = useState<number | null>(null);
  const [adaptHistory, setAdaptHistory] = useState<Record<string, unknown>[]>([]);

  const isAutoMode = strategyType === "auto";
  const { toast } = useToast();

  const { lastMessage } = useWebSocket("/ws/optimize");

  // Initialize param grid when strategy type changes
  useEffect(() => {
    if (strategyType === "auto") {
      setParamGrid({});
      return;
    }
    const grid = DEFAULT_GRIDS[strategyType] || {};
    const gridStrings: Record<string, string> = {};
    for (const [k, v] of Object.entries(grid)) {
      gridStrings[k] = v.join(", ");
    }
    setParamGrid(gridStrings);
  }, [strategyType]);

  // Load job history
  useEffect(() => {
    api.get<JobSummary[]>("/api/optimize/").then(setJobs).catch(() => toast.error("Failed to load optimization history"));
  }, []);

  const loadAdaptations = () => {
    api.get<Record<string, unknown>[]>("/api/optimize/live").then(setAdaptations).catch(() => toast.error("Failed to load adaptations"));
  };

  const createAdaptation = async () => {
    try {
      await api.post("/api/optimize/live", { strategy_type: adaptStrategy });
      toast.success("Adaptation created");
      loadAdaptations();
    } catch {
      toast.error("Failed to create adaptation");
    }
  };

  const stopAdaptation = async (id: number) => {
    try {
      await api.delete(`/api/optimize/live/${id}`);
      toast.success("Adaptation stopped");
      loadAdaptations();
    } catch {
      toast.error("Failed to stop adaptation");
    }
  };

  const loadAdaptHistory = async (id: number) => {
    if (expandedAdaptId === id) {
      setExpandedAdaptId(null);
      return;
    }
    try {
      const res = await api.get<Record<string, unknown>[]>(`/api/optimize/live/${id}/history`);
      setAdaptHistory(res);
      setExpandedAdaptId(id);
    } catch {
      setAdaptHistory([]);
      setExpandedAdaptId(id);
    }
  };

  // Handle WS progress
  useEffect(() => {
    if (!lastMessage) return;
    try {
      const data = JSON.parse(lastMessage);
      if (data.status === "running" && data.combo) {
        setProgress({ combo: data.combo, total: data.total });
        if (data.current_strategy) {
          setSweepProgress({
            current_strategy: data.current_strategy,
            strategy_index: data.strategy_index,
            total_strategies: data.total_strategies,
            combo: data.combo,
            total: data.total,
          });
        }
      }
      if (data.status === "complete" || data.status === "cancelled") {
        setRunning(false);
        setProgress(null);
        setSweepProgress(null);
        api.get<JobSummary[]>("/api/optimize/").then(setJobs).catch(() => {});
      }
    } catch {}
  }, [lastMessage]);

  const parseGrid = (): Record<string, (number | string)[]> => {
    const parsed: Record<string, (number | string)[]> = {};
    for (const [key, val] of Object.entries(paramGrid)) {
      const values = val.split(",").map((v) => v.trim()).filter(Boolean);
      parsed[key] = values.map((v) => {
        const n = Number(v);
        return isNaN(n) ? v : n;
      });
    }
    return parsed;
  };

  const runOptimization = async () => {
    setRunning(true);
    setResults([]);
    setSweepResults(null);
    setProgress(null);
    setSweepProgress(null);
    try {
      const endpoint = isAutoMode ? "/api/optimize/sweep" : "/api/optimize/strategy";
      const body = isAutoMode
        ? {
            symbols: symbols.split(",").map((s) => s.trim()),
            start,
            end,
            n_splits: nSplits,
            train_ratio: trainRatio,
          }
        : {
            strategy_type: strategyType,
            symbols: symbols.split(",").map((s) => s.trim()),
            start,
            end,
            param_grid: parseGrid(),
            n_splits: nSplits,
            train_ratio: trainRatio,
          };
      const res = await api.post<{ job_id: number }>(endpoint, body);
      setSelectedJobId(res.job_id);
      // Poll for results since WS may not always deliver
      const poll = setInterval(async () => {
        try {
          const job = await api.get<{
            status: string;
            job_type?: string;
            results?: OptResult[] | SweepResults;
          }>(`/api/optimize/${res.job_id}`);
          if (job.status === "complete" || job.status === "cancelled" || job.status === "error") {
            clearInterval(poll);
            setRunning(false);
            setProgress(null);
            setSweepProgress(null);
            if (job.results) {
              if (job.job_type === "sweep" && !Array.isArray(job.results)) {
                setSweepResults(job.results as SweepResults);
              } else if (Array.isArray(job.results)) {
                setResults(job.results as OptResult[]);
              }
            }
            api.get<JobSummary[]>("/api/optimize/").then(setJobs).catch(() => {});
          }
        } catch {
          clearInterval(poll);
          setRunning(false);
        }
      }, 3000);
    } catch {
      setRunning(false);
      toast.error("Failed to start optimization");
    }
  };

  const loadJobResults = async (jobId: number) => {
    setSelectedJobId(jobId);
    try {
      const job = await api.get<{
        job_type?: string;
        results?: OptResult[] | SweepResults;
      }>(`/api/optimize/${jobId}`);
      if (job.results) {
        if (job.job_type === "sweep" && !Array.isArray(job.results)) {
          setSweepResults(job.results as SweepResults);
          setResults([]);
        } else if (Array.isArray(job.results)) {
          setResults(job.results as OptResult[]);
          setSweepResults(null);
        }
      }
    } catch {
      toast.error("Failed to load job results");
    }
  };

  const cancelJob = async () => {
    if (selectedJobId) {
      await api.delete(`/api/optimize/${selectedJobId}`);
      setRunning(false);
      setProgress(null);
    }
  };

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(key === "rank");
    }
  };

  const sortedResults = [...results].sort((a, b) => {
    const dir = sortAsc ? 1 : -1;
    return (a[sortKey] - b[sortKey]) * dir;
  });

  const backtestWithParams = (params: Record<string, unknown>, overrideStrategy?: string) => {
    const st = overrideStrategy || strategyType;
    const query = new URLSearchParams({
      strategy_type: st,
      params: JSON.stringify(params),
      symbols,
      start,
      end,
    });
    window.location.href = `/backtest?${query.toString()}`;
  };

  const saveAsStrategy = async (params: Record<string, unknown>, overrideStrategy?: string) => {
    const st = overrideStrategy || strategyType;
    try {
      await api.post("/api/strategies/", {
        name: `${st}_optimized`,
        strategy_type: st,
        params,
      });
      toast.success("Strategy saved!");
    } catch {
      toast.error("Failed to save strategy");
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Optimize</h1>

      {/* Configuration Form */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Strategy Type</label>
            <select
              value={strategyType}
              onChange={(e) => setStrategyType(e.target.value)}
              className="border rounded px-3 py-2 w-full"
            >
              <option value="auto">Auto (all strategies)</option>
              <option value="momentum">Momentum</option>
              <option value="mean_reversion">Mean Reversion</option>
              <option value="stat_arb">Stat Arb</option>
              <option value="market_making">Market Making</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Symbols</label>
            <input
              className="border rounded px-3 py-2 w-full"
              placeholder="SPY"
              value={symbols}
              onChange={(e) => setSymbols(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Start</label>
            <input
              type="date"
              className="border rounded px-3 py-2 w-full"
              value={start}
              onChange={(e) => setStart(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">End</label>
            <input
              type="date"
              className="border rounded px-3 py-2 w-full"
              value={end}
              onChange={(e) => setEnd(e.target.value)}
            />
          </div>
        </div>

        {/* Parameter Grid */}
        {isAutoMode ? (
          <div className="mb-4 p-3 bg-blue-50 rounded text-sm text-blue-700">
            Auto mode will evaluate all 4 strategy types using default parameter grids.
          </div>
        ) : (
          <div className="mb-4">
            <h3 className="text-sm font-medium mb-2">Parameter Grid</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {Object.entries(paramGrid).map(([key, val]) => (
                <div key={key} className="flex gap-2 items-center">
                  <label className="text-sm w-32 text-gray-600">{key}</label>
                  <input
                    className="border rounded px-3 py-1 flex-1 text-sm"
                    value={val}
                    onChange={(e) => setParamGrid({ ...paramGrid, [key]: e.target.value })}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Advanced Settings */}
        <div className="mb-4">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-blue-600 hover:underline"
          >
            {showAdvanced ? "Hide" : "Show"} Advanced Settings
          </button>
          {showAdvanced && (
            <div className="grid grid-cols-2 gap-3 mt-2">
              <div>
                <label className="block text-sm font-medium mb-1">Walk-Forward Splits</label>
                <input
                  type="number"
                  className="border rounded px-3 py-2 w-full"
                  value={nSplits}
                  onChange={(e) => setNSplits(Number(e.target.value))}
                  min={2}
                  max={20}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Train Ratio</label>
                <input
                  type="number"
                  className="border rounded px-3 py-2 w-full"
                  value={trainRatio}
                  onChange={(e) => setTrainRatio(Number(e.target.value))}
                  step={0.05}
                  min={0.5}
                  max={0.9}
                />
              </div>
            </div>
          )}
        </div>

        {/* Run / Cancel */}
        <div className="flex gap-3">
          <button
            onClick={runOptimization}
            disabled={running}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {running ? "Running..." : "Run Optimization"}
          </button>
          {running && (
            <button
              onClick={cancelJob}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Cancel
            </button>
          )}
        </div>

        {/* Progress */}
        {progress && (
          <div className="mt-4">
            {sweepProgress && (
              <div className="text-sm font-medium mb-2">
                Strategy {sweepProgress.strategy_index}/{sweepProgress.total_strategies}: {sweepProgress.current_strategy}
              </div>
            )}
            <div className="flex justify-between text-sm mb-1">
              <span>
                {progress.combo}/{progress.total} combinations
              </span>
              <span>{Math.round((progress.combo / progress.total) * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${(progress.combo / progress.total) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Results Table */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <h2 className="text-lg font-semibold mb-3">Results</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  {(
                    [
                      ["rank", "Rank"],
                      ["mean_sharpe", "Sharpe"],
                      ["mean_return", "Return"],
                      ["max_drawdown", "Max DD"],
                      ["mean_win_rate", "Win Rate"],
                    ] as [SortKey, string][]
                  ).map(([key, label]) => (
                    <th
                      key={key}
                      className="py-2 px-2 cursor-pointer hover:text-gray-700"
                      onClick={() => handleSort(key)}
                    >
                      {label} {sortKey === key ? (sortAsc ? "▲" : "▼") : ""}
                    </th>
                  ))}
                  <th className="py-2 px-2">Params</th>
                  <th className="py-2 px-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedResults.map((r) => (
                  <tr key={r.rank} className="border-t hover:bg-gray-50">
                    <td className="py-2 px-2">{r.rank}</td>
                    <td className="py-2 px-2">{r.mean_sharpe.toFixed(3)}</td>
                    <td className="py-2 px-2">{(r.mean_return * 100).toFixed(2)}%</td>
                    <td className="py-2 px-2">{(r.max_drawdown * 100).toFixed(2)}%</td>
                    <td className="py-2 px-2">{(r.mean_win_rate * 100).toFixed(1)}%</td>
                    <td className="py-2 px-2 text-xs font-mono">
                      {JSON.stringify(r.params)}
                    </td>
                    <td className="py-2 px-2">
                      <div className="flex gap-1">
                        <button
                          onClick={() => backtestWithParams(r.params)}
                          className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                        >
                          Backtest
                        </button>
                        <button
                          onClick={() => saveAsStrategy(r.params)}
                          className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                        >
                          Save as Strategy
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Sweep Comparison Table */}
      {sweepResults && sweepResults.by_strategy && (
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <h2 className="text-lg font-semibold mb-3">Strategy Comparison</h2>
          {sweepResults.recommendation && sweepResults.recommendation.strategy_type && (
            <div className="mb-3 p-3 bg-green-50 rounded text-sm">
              <span className="font-medium">Recommended:</span>{" "}
              {sweepResults.recommendation.strategy_type} (Sharpe: {sweepResults.recommendation.mean_sharpe.toFixed(3)}, Confidence: {sweepResults.recommendation.confidence})
            </div>
          )}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="py-2 px-2">Strategy</th>
                  <th className="py-2 px-2">Best Sharpe</th>
                  <th className="py-2 px-2">Best Return</th>
                  <th className="py-2 px-2">Max DD</th>
                  <th className="py-2 px-2">Best Params</th>
                  <th className="py-2 px-2">Status</th>
                  <th className="py-2 px-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(sweepResults.by_strategy)
                  .sort(([, a], [, b]) => {
                    const aS = a[0]?.mean_sharpe ?? -Infinity;
                    const bS = b[0]?.mean_sharpe ?? -Infinity;
                    return bS - aS;
                  })
                  .map(([st, stratResults]) => {
                    const best = stratResults[0];
                    const isRecommended = sweepResults.recommendation?.strategy_type === st;
                    if (!best) return null;
                    return (
                      <tr key={st} className="border-t">
                        <td className="py-2 px-2">
                          <button
                            className="text-blue-600 hover:underline font-medium"
                            onClick={() => setExpandedStrategy(expandedStrategy === st ? null : st)}
                          >
                            {expandedStrategy === st ? "▼" : "▶"} {st}
                          </button>
                          {isRecommended && (
                            <span className="ml-2 text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">
                              Recommended
                            </span>
                          )}
                        </td>
                        <td className="py-2 px-2">{best.mean_sharpe.toFixed(3)}</td>
                        <td className="py-2 px-2">{(best.mean_return * 100).toFixed(2)}%</td>
                        <td className="py-2 px-2">{(best.max_drawdown * 100).toFixed(2)}%</td>
                        <td className="py-2 px-2 text-xs font-mono">{JSON.stringify(best.params)}</td>
                        <td className="py-2 px-2">
                          {best.recommended === false ? (
                            <span className="text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded">Not recommended</span>
                          ) : (
                            <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">OK</span>
                          )}
                        </td>
                        <td className="py-2 px-2">
                          <div className="flex gap-1">
                            <button
                              onClick={() => backtestWithParams(best.params, st)}
                              className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                            >
                              Backtest
                            </button>
                            <button
                              onClick={() => saveAsStrategy(best.params, st)}
                              className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                            >
                              Save as Strategy
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>

          {/* Expanded strategy detail */}
          {expandedStrategy && sweepResults.by_strategy[expandedStrategy] && (
            <div className="mt-4 border-t pt-4">
              <h3 className="text-sm font-medium mb-2">Top results for {expandedStrategy}</h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="py-1 px-2">Rank</th>
                    <th className="py-1 px-2">Sharpe</th>
                    <th className="py-1 px-2">Return</th>
                    <th className="py-1 px-2">Max DD</th>
                    <th className="py-1 px-2">Win Rate</th>
                    <th className="py-1 px-2">Params</th>
                    <th className="py-1 px-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sweepResults.by_strategy[expandedStrategy].map((r) => (
                    <tr key={r.rank} className="border-t hover:bg-gray-50">
                      <td className="py-1 px-2">{r.rank}</td>
                      <td className="py-1 px-2">{r.mean_sharpe.toFixed(3)}</td>
                      <td className="py-1 px-2">{(r.mean_return * 100).toFixed(2)}%</td>
                      <td className="py-1 px-2">{(r.max_drawdown * 100).toFixed(2)}%</td>
                      <td className="py-1 px-2">{(r.mean_win_rate * 100).toFixed(1)}%</td>
                      <td className="py-1 px-2 text-xs font-mono">{JSON.stringify(r.params)}</td>
                      <td className="py-1 px-2">
                        <div className="flex gap-1">
                          <button
                            onClick={() => backtestWithParams(r.params, expandedStrategy)}
                            className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                          >
                            Backtest
                          </button>
                          <button
                            onClick={() => saveAsStrategy(r.params, expandedStrategy)}
                            className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
                          >
                            Save as Strategy
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Job History */}
      {jobs.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">Optimization History</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="py-2">ID</th>
                <th className="py-2">Type</th>
                <th className="py-2">Strategy</th>
                <th className="py-2">Status</th>
                <th className="py-2">Best Sharpe</th>
                <th className="py-2">Date</th>
                <th className="py-2"></th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.id} className="border-t hover:bg-gray-50">
                  <td className="py-2">{j.id}</td>
                  <td className="py-2">{j.job_type}</td>
                  <td className="py-2">{j.strategy_type}</td>
                  <td className="py-2">
                    <span
                      className={`px-2 py-0.5 rounded text-xs ${
                        j.status === "complete"
                          ? "bg-green-100 text-green-700"
                          : j.status === "running"
                            ? "bg-blue-100 text-blue-700"
                            : j.status === "error"
                              ? "bg-red-100 text-red-700"
                              : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {j.status}
                    </span>
                  </td>
                  <td className="py-2">{j.best_sharpe?.toFixed(3) ?? "-"}</td>
                  <td className="py-2 text-gray-500">{j.created_at.split("T")[0]}</td>
                  <td className="py-2">
                    {j.status === "complete" && (
                      <button
                        onClick={() => loadJobResults(j.id)}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        View Results
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Live Adaptation */}
      <div className="bg-white rounded-lg shadow p-4 mt-6">
        <button
          onClick={() => { setShowAdaptation(!showAdaptation); if (!showAdaptation) loadAdaptations(); }}
          className="text-lg font-semibold w-full text-left"
        >
          {showAdaptation ? "▼" : "▶"} Live Adaptation
        </button>
        {showAdaptation && (
          <div className="mt-4">
            {/* Create form */}
            <div className="flex gap-3 mb-4 items-end">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Strategy</label>
                <select
                  value={adaptStrategy}
                  onChange={(e) => setAdaptStrategy(e.target.value)}
                  className="border rounded px-3 py-2"
                >
                  <option value="momentum">Momentum</option>
                  <option value="mean_reversion">Mean Reversion</option>
                  <option value="stat_arb">Stat Arb</option>
                  <option value="market_making">Market Making</option>
                </select>
              </div>
              <button onClick={createAdaptation} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                Create Adaptation
              </button>
            </div>

            {/* Active adaptations table */}
            {adaptations.length === 0 ? (
              <p className="text-gray-500 text-sm">No active adaptations</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="py-2">ID</th>
                    <th className="py-2">Strategy</th>
                    <th className="py-2">Next Run</th>
                    <th className="py-2">Status</th>
                    <th className="py-2"></th>
                  </tr>
                </thead>
                <tbody>
                  {adaptations.map((a) => (
                    <>
                      <tr key={Number(a.id)} className="border-t hover:bg-gray-50">
                        <td className="py-2">
                          <button className="text-blue-600 hover:underline" onClick={() => loadAdaptHistory(Number(a.id))}>
                            {expandedAdaptId === Number(a.id) ? "▼" : "▶"} {String(a.id)}
                          </button>
                        </td>
                        <td className="py-2">{String(a.strategy_type)}</td>
                        <td className="py-2 text-gray-500">{String(a.next_run || "-")}</td>
                        <td className="py-2">{String(a.status || "active")}</td>
                        <td className="py-2">
                          <button
                            onClick={() => stopAdaptation(Number(a.id))}
                            className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded hover:bg-red-200"
                          >
                            Stop
                          </button>
                        </td>
                      </tr>
                      {expandedAdaptId === Number(a.id) && (
                        <tr key={`history-${a.id}`}>
                          <td colSpan={5} className="py-2 px-4 bg-gray-50">
                            {adaptHistory.length === 0 ? (
                              <p className="text-gray-500 text-sm">No adaptation events yet</p>
                            ) : (
                              <table className="w-full text-xs">
                                <thead>
                                  <tr className="text-left text-gray-400">
                                    <th className="py-1">Trigger</th>
                                    <th className="py-1">Proposed</th>
                                    <th className="py-1">Applied</th>
                                    <th className="py-1">Status</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {adaptHistory.map((h, i) => (
                                    <tr key={i} className="border-t">
                                      <td className="py-1">{String(h.trigger_type)}</td>
                                      <td className="py-1 font-mono">{JSON.stringify(h.proposed_params)}</td>
                                      <td className="py-1 font-mono">{JSON.stringify(h.applied_params)}</td>
                                      <td className="py-1">{String(h.status)}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            )}
                          </td>
                        </tr>
                      )}
                    </>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
