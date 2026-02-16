"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function TradesPage() {
  const [trades, setTrades] = useState<Record<string, unknown>[]>([]);
  const [pnl, setPnl] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    api.get<Record<string, unknown>[]>("/api/monitor/trades").then(setTrades).catch(() => {});
    api.get<Record<string, unknown>>("/api/monitor/pnl").then(setPnl).catch(() => {});
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Trades</h1>
      {pnl && (
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <h2 className="text-lg font-semibold mb-3">P&L Summary</h2>
          <pre className="text-sm bg-gray-50 p-3 rounded">{JSON.stringify(pnl, null, 2)}</pre>
        </div>
      )}
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-3">Trade History</h2>
        {trades.length === 0 ? (
          <p className="text-gray-500">No trades recorded</p>
        ) : (
          <table className="w-full text-sm">
            <thead><tr className="text-left text-gray-500"><th>Symbol</th><th>Side</th><th>Qty</th><th>Price</th><th>Time</th></tr></thead>
            <tbody>
              {trades.map((t, i) => (
                <tr key={i} className="border-t">
                  <td>{String(t.symbol)}</td>
                  <td>{String(t.side)}</td>
                  <td>{String(t.qty)}</td>
                  <td>{String(t.price)}</td>
                  <td>{String(t.timestamp)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
