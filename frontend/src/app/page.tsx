"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { api } from "@/lib/api";
import { useWebSocket } from "@/hooks/useWebSocket";

interface PriceEntry {
  price: number;
  prev: number | null;
  timestamp: number;
}

const WATCHLIST = ["SPY", "QQQ", "AAPL", "MSFT"];

export default function Dashboard() {
  const [positions, setPositions] = useState<Record<string, unknown>[]>([]);
  const [trades, setTrades] = useState<Record<string, unknown>[]>([]);
  const [activeStrategies, setActiveStrategies] = useState<Record<string, unknown>[]>([]);
  const [goals, setGoals] = useState<Record<string, unknown>[]>([]);
  const [alerts, setAlerts] = useState<Record<string, unknown>[]>([]);
  const [prices, setPrices] = useState<Map<string, PriceEntry>>(new Map());
  const [account, setAccount] = useState<Record<string, unknown> | null>(null);
  const [accountError, setAccountError] = useState(false);
  const [liveTrades, setLiveTrades] = useState<Record<string, unknown>[]>([]);
  const { lastMessage: alertMsg } = useWebSocket("/ws/alerts");
  const { lastMessage: priceMsg, send: priceSend } = useWebSocket("/ws/prices");
  const { lastMessage: tradeMsg, isConnected: tradeWsConnected } = useWebSocket("/ws/trades");
  const subscribedRef = useRef(false);

  const subscribeToPrices = useCallback(() => {
    if (subscribedRef.current || !priceSend) return;
    for (const sym of WATCHLIST) {
      priceSend(JSON.stringify({ action: "subscribe", symbol: sym }));
    }
    subscribedRef.current = true;
  }, [priceSend]);

  useEffect(() => {
    if (priceMsg) {
      const data = JSON.parse(priceMsg);
      if (data.status === "connected") {
        subscribeToPrices();
        return;
      }
      if (data.symbol && data.price != null) {
        setPrices((prev) => {
          const next = new Map(prev);
          const existing = next.get(data.symbol);
          next.set(data.symbol, {
            price: data.price,
            prev: existing?.price ?? null,
            timestamp: data.timestamp,
          });
          return next;
        });
      }
    }
  }, [priceMsg, subscribeToPrices]);

  useEffect(() => {
    api.get<Record<string, unknown>[]>("/api/broker/positions").then(setPositions).catch(() => {});
    api.get<Record<string, unknown>[]>("/api/monitor/trades").then(setTrades).catch(() => {});
    api.get<Record<string, unknown>[]>("/api/strategies/live/active").then(setActiveStrategies).catch(() => {});
    api.get<Record<string, unknown>[]>("/api/portfolio/goals/").then(setGoals).catch(() => {});
    api.get<Record<string, unknown>[]>("/api/alerts/history").then(setAlerts).catch(() => {});
    api.get<Record<string, unknown>>("/api/broker/account").then(setAccount).catch(() => setAccountError(true));
  }, []);

  useEffect(() => {
    if (tradeMsg) {
      try {
        const data = JSON.parse(tradeMsg);
        if (data.symbol) {
          setLiveTrades((prev) => [data, ...prev].slice(0, 10));
        }
      } catch {}
    }
  }, [tradeMsg]);

  useEffect(() => {
    if (alertMsg) {
      const data = JSON.parse(alertMsg);
      setAlerts((prev) => [data, ...prev].slice(0, 20));
    }
  }, [alertMsg]);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Account */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">Account</h2>
          {accountError ? (
            <p className="text-gray-500">Broker not connected</p>
          ) : account ? (
            <div className="grid grid-cols-3 gap-2">
              {[["Cash", account.cash], ["Portfolio Value", account.portfolio_value], ["Buying Power", account.buying_power]].map(([label, val]) => (
                <div key={String(label)} className="text-center">
                  <div className="text-xs text-gray-500">{String(label)}</div>
                  <div className="text-lg font-semibold">${Number(val).toLocaleString()}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">Loading...</p>
          )}
        </div>

        {/* Live Trade Feed */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">
            Live Trade Feed
            {!tradeWsConnected && <span className="ml-2 text-xs text-red-500">Disconnected</span>}
          </h2>
          {liveTrades.length === 0 ? (
            <p className="text-gray-500">No live trades</p>
          ) : (
            <table className="w-full text-sm">
              <thead><tr className="text-left text-gray-500"><th>Symbol</th><th>Side</th><th>Qty</th><th>Price</th></tr></thead>
              <tbody>
                {liveTrades.map((t, i) => (
                  <tr key={i} className="border-t">
                    <td>{String(t.symbol)}</td><td>{String(t.side)}</td>
                    <td>{String(t.qty)}</td><td>{String(t.price)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Portfolio */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">Portfolio</h2>
          {positions.length === 0 ? (
            <p className="text-gray-500">No positions</p>
          ) : (
            <table className="w-full text-sm">
              <thead><tr className="text-left text-gray-500"><th>Symbol</th><th>Qty</th><th>Avg</th><th>Current</th></tr></thead>
              <tbody>
                {positions.map((p, i) => (
                  <tr key={i} className="border-t">
                    <td>{String(p.symbol)}</td><td>{String(p.qty)}</td>
                    <td>{String(p.avg_price)}</td><td>{String(p.current_price)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Live Prices */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">Live Prices</h2>
          {prices.size === 0 ? (
            <p className="text-gray-500">Connecting...</p>
          ) : (
            <table className="w-full text-sm">
              <thead><tr className="text-left text-gray-500"><th>Symbol</th><th className="text-right">Price</th></tr></thead>
              <tbody>
                {WATCHLIST.map((sym) => {
                  const entry = prices.get(sym);
                  if (!entry) return null;
                  const direction = entry.prev == null ? null : entry.price > entry.prev ? "up" : entry.price < entry.prev ? "down" : null;
                  return (
                    <tr key={sym} className="border-t">
                      <td className="font-medium">{sym}</td>
                      <td className={`text-right ${direction === "up" ? "text-green-600" : direction === "down" ? "text-red-600" : ""}`}>
                        {direction === "up" && "\u25B2 "}{direction === "down" && "\u25BC "}{entry.price.toFixed(2)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Active Strategies */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">Active Strategies</h2>
          {activeStrategies.length === 0 ? (
            <p className="text-gray-500">No active strategies</p>
          ) : (
            <table className="w-full text-sm">
              <thead><tr className="text-left text-gray-500"><th>Name</th><th>Type</th><th>Mode</th></tr></thead>
              <tbody>
                {activeStrategies.map((s, i) => (
                  <tr key={i} className="border-t">
                    <td>{String(s.name)}</td><td>{String(s.strategy_type)}</td>
                    <td><span className={`px-2 py-0.5 rounded text-xs ${s.mode === "auto-trade" ? "bg-red-100 text-red-700" : s.mode === "alert" ? "bg-yellow-100 text-yellow-700" : "bg-gray-100 text-gray-600"}`}>{String(s.mode)}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Portfolio Goals */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">Portfolio Goals</h2>
          {goals.length === 0 ? (
            <p className="text-gray-500">No goals set</p>
          ) : (
            <ul className="text-sm space-y-2">
              {goals.map((g, i) => (
                <li key={i} className="flex justify-between border-b pb-1">
                  <span>{String(g.name)}</span>
                  <span className="text-gray-500">drift: {String(g.drift_threshold)}%</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Recent Trades */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">Recent Trades</h2>
          {trades.length === 0 ? (
            <p className="text-gray-500">No trades yet</p>
          ) : (
            <table className="w-full text-sm">
              <thead><tr className="text-left text-gray-500"><th>Symbol</th><th>Side</th><th>Qty</th><th>Price</th></tr></thead>
              <tbody>
                {trades.map((t, i) => (
                  <tr key={i} className="border-t">
                    <td>{String(t.symbol)}</td><td>{String(t.side)}</td>
                    <td>{String(t.qty)}</td><td>{String(t.price)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Alert Feed */}
        <div className="bg-white rounded-lg shadow p-4 md:col-span-2">
          <h2 className="text-lg font-semibold mb-3">Recent Alerts</h2>
          {alerts.length === 0 ? (
            <p className="text-gray-500">No alerts</p>
          ) : (
            <ul className="text-sm space-y-1 max-h-48 overflow-y-auto">
              {alerts.map((a, i) => (
                <li key={i} className="flex justify-between border-b pb-1">
                  <span>{String(a.message)}</span>
                  <span className="text-gray-400 text-xs">{String(a.triggered_at || "")}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
