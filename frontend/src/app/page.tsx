"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function Dashboard() {
  const [positions, setPositions] = useState<Record<string, unknown>[]>([]);
  const [trades, setTrades] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    api.get<Record<string, unknown>[]>("/api/broker/positions").then(setPositions).catch(() => {});
    api.get<Record<string, unknown>[]>("/api/monitor/trades").then(setTrades).catch(() => {});
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">Portfolio</h2>
          {positions.length === 0 ? (
            <p className="text-gray-500">No positions</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500">
                  <th>Symbol</th><th>Qty</th><th>Avg Price</th><th>Current</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p, i) => (
                  <tr key={i} className="border-t">
                    <td>{String(p.symbol)}</td>
                    <td>{String(p.qty)}</td>
                    <td>{String(p.avg_price)}</td>
                    <td>{String(p.current_price)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-lg font-semibold mb-3">Recent Trades</h2>
          {trades.length === 0 ? (
            <p className="text-gray-500">No trades yet</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500">
                  <th>Symbol</th><th>Side</th><th>Qty</th><th>Price</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((t, i) => (
                  <tr key={i} className="border-t">
                    <td>{String(t.symbol)}</td>
                    <td>{String(t.side)}</td>
                    <td>{String(t.qty)}</td>
                    <td>{String(t.price)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
