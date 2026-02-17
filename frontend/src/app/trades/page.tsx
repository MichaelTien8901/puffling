"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function TradesPage() {
  const [trades, setTrades] = useState<Record<string, unknown>[]>([]);
  const [pnl, setPnl] = useState<Record<string, unknown> | null>(null);

  // Order form state
  const [symbol, setSymbol] = useState("");
  const [side, setSide] = useState("BUY");
  const [qty, setQty] = useState("");
  const [orderType, setOrderType] = useState("market");
  const [submitting, setSubmitting] = useState(false);
  const [orderResult, setOrderResult] = useState<{ ok: boolean; message: string } | null>(null);

  const loadData = () => {
    api.get<Record<string, unknown>[]>("/api/monitor/trades").then(setTrades).catch(() => {});
    api.get<Record<string, unknown>>("/api/monitor/pnl").then(setPnl).catch(() => {});
  };

  useEffect(() => { loadData(); }, []);

  const submitOrder = async () => {
    if (!symbol || !qty) return;
    setSubmitting(true);
    setOrderResult(null);
    try {
      const res = await api.post<Record<string, unknown>>("/api/broker/order", {
        symbol: symbol.toUpperCase(),
        side,
        qty: parseFloat(qty),
        order_type: orderType,
      });
      setOrderResult({ ok: true, message: `Order submitted: ${side} ${qty} ${symbol.toUpperCase()}` });
      setSymbol("");
      setQty("");
      // Refresh trades after a short delay
      setTimeout(loadData, 2000);
    } catch (e) {
      setOrderResult({ ok: false, message: "Order failed. Check broker connection and inputs." });
    }
    setSubmitting(false);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Trades</h1>

      {/* Order Entry Form */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">New Order</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-3">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Symbol</label>
            <input
              className="border rounded px-3 py-2 w-full"
              placeholder="SPY"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Side</label>
            <select
              className="border rounded px-3 py-2 w-full"
              value={side}
              onChange={(e) => setSide(e.target.value)}
            >
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Quantity</label>
            <input
              type="number"
              className="border rounded px-3 py-2 w-full"
              placeholder="10"
              value={qty}
              onChange={(e) => setQty(e.target.value)}
              min="0"
              step="1"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Order Type</label>
            <select
              className="border rounded px-3 py-2 w-full"
              value={orderType}
              onChange={(e) => setOrderType(e.target.value)}
            >
              <option value="market">Market</option>
              <option value="limit">Limit</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={submitOrder}
              disabled={submitting || !symbol || !qty}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50 w-full"
            >
              {submitting ? "Submitting..." : "Submit Order"}
            </button>
          </div>
        </div>
        {orderResult && (
          <div className={`text-sm px-3 py-2 rounded ${orderResult.ok ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
            {orderResult.message}
          </div>
        )}
      </div>

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
