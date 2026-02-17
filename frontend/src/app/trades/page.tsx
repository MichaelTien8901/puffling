"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type AssetType = "STK" | "OPT" | "FUT" | "CASH";

export default function TradesPage() {
  const [trades, setTrades] = useState<Record<string, unknown>[]>([]);
  const [pnl, setPnl] = useState<Record<string, unknown> | null>(null);

  // Order form state
  const [symbol, setSymbol] = useState("");
  const [side, setSide] = useState("BUY");
  const [qty, setQty] = useState("");
  const [orderType, setOrderType] = useState("market");
  const [assetType, setAssetType] = useState<AssetType>("STK");

  // Multi-asset fields
  const [exchange, setExchange] = useState("SMART");
  const [currency, setCurrency] = useState("USD");
  const [expiry, setExpiry] = useState("");
  const [strike, setStrike] = useState("");
  const [right, setRight] = useState("C");
  const [multiplier, setMultiplier] = useState("");
  const [pairCurrency, setPairCurrency] = useState("");
  const [limitPrice, setLimitPrice] = useState("");
  const [stopPrice, setStopPrice] = useState("");
  const [timeInForce, setTimeInForce] = useState("DAY");

  const [submitting, setSubmitting] = useState(false);
  const [orderResult, setOrderResult] = useState<{ ok: boolean; message: string } | null>(null);

  const showAdvanced = assetType !== "STK" || orderType !== "market";

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
      const body: Record<string, unknown> = {
        symbol: symbol.toUpperCase(),
        side,
        qty: parseFloat(qty),
        order_type: orderType,
        asset_type: assetType,
        exchange,
        currency,
      };
      if (assetType === "OPT") {
        if (expiry) body.expiry = expiry;
        if (strike) body.strike = parseFloat(strike);
        body.right = right;
        if (multiplier) body.multiplier = parseInt(multiplier);
      }
      if (assetType === "FUT") {
        if (expiry) body.expiry = expiry;
        if (multiplier) body.multiplier = parseInt(multiplier);
      }
      if (assetType === "CASH" && pairCurrency) {
        body.pair_currency = pairCurrency;
      }
      if (orderType === "limit" || orderType === "stop_limit") {
        if (limitPrice) body.limit_price = parseFloat(limitPrice);
      }
      if (orderType === "stop" || orderType === "stop_limit") {
        if (stopPrice) body.stop_price = parseFloat(stopPrice);
      }
      if (orderType !== "market") {
        body.time_in_force = timeInForce;
      }

      const res = await api.post<Record<string, unknown>>("/api/broker/order", body);
      const summary = res.summary ? String(res.summary) : `${side} ${qty} ${symbol.toUpperCase()}`;
      setOrderResult({ ok: true, message: `Order submitted: ${summary}` });
      setSymbol("");
      setQty("");
      setExpiry("");
      setStrike("");
      setMultiplier("");
      setPairCurrency("");
      setLimitPrice("");
      setStopPrice("");
      setTimeout(loadData, 2000);
    } catch {
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
              <option value="stop">Stop</option>
              <option value="stop_limit">Stop Limit</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Asset Type</label>
            <select
              data-testid="asset-type"
              className="border rounded px-3 py-2 w-full"
              value={assetType}
              onChange={(e) => setAssetType(e.target.value as AssetType)}
            >
              <option value="STK">Stock</option>
              <option value="OPT">Option</option>
              <option value="FUT">Future</option>
              <option value="CASH">Forex</option>
            </select>
          </div>
        </div>

        {showAdvanced && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3 border-t pt-3">
            {(assetType === "OPT" || assetType === "FUT") && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Expiry</label>
                <input
                  type="date"
                  data-testid="expiry"
                  className="border rounded px-3 py-2 w-full"
                  value={expiry}
                  onChange={(e) => setExpiry(e.target.value)}
                />
              </div>
            )}
            {assetType === "OPT" && (
              <>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Strike</label>
                  <input
                    type="number"
                    data-testid="strike"
                    className="border rounded px-3 py-2 w-full"
                    placeholder="450"
                    value={strike}
                    onChange={(e) => setStrike(e.target.value)}
                    min="0"
                    step="0.5"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Right</label>
                  <select
                    data-testid="right"
                    className="border rounded px-3 py-2 w-full"
                    value={right}
                    onChange={(e) => setRight(e.target.value)}
                  >
                    <option value="C">Call</option>
                    <option value="P">Put</option>
                  </select>
                </div>
              </>
            )}
            {(assetType === "OPT" || assetType === "FUT") && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Multiplier</label>
                <input
                  type="number"
                  className="border rounded px-3 py-2 w-full"
                  placeholder="100"
                  value={multiplier}
                  onChange={(e) => setMultiplier(e.target.value)}
                  min="1"
                />
              </div>
            )}
            {assetType === "CASH" && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Pair Currency</label>
                <input
                  className="border rounded px-3 py-2 w-full"
                  placeholder="CAD"
                  value={pairCurrency}
                  onChange={(e) => setPairCurrency(e.target.value)}
                />
              </div>
            )}
            {assetType !== "STK" && (
              <>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Exchange</label>
                  <input
                    className="border rounded px-3 py-2 w-full"
                    value={exchange}
                    onChange={(e) => setExchange(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">Currency</label>
                  <input
                    className="border rounded px-3 py-2 w-full"
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                  />
                </div>
              </>
            )}
            {(orderType === "limit" || orderType === "stop_limit") && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Limit Price</label>
                <input
                  type="number"
                  className="border rounded px-3 py-2 w-full"
                  placeholder="0.00"
                  value={limitPrice}
                  onChange={(e) => setLimitPrice(e.target.value)}
                  min="0"
                  step="0.01"
                />
              </div>
            )}
            {(orderType === "stop" || orderType === "stop_limit") && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Stop Price</label>
                <input
                  type="number"
                  className="border rounded px-3 py-2 w-full"
                  placeholder="0.00"
                  value={stopPrice}
                  onChange={(e) => setStopPrice(e.target.value)}
                  min="0"
                  step="0.01"
                />
              </div>
            )}
            {orderType !== "market" && (
              <div>
                <label className="block text-sm text-gray-600 mb-1">Time in Force</label>
                <select
                  className="border rounded px-3 py-2 w-full"
                  value={timeInForce}
                  onChange={(e) => setTimeInForce(e.target.value)}
                >
                  <option value="DAY">DAY</option>
                  <option value="GTC">GTC</option>
                  <option value="IOC">IOC</option>
                  <option value="FOK">FOK</option>
                </select>
              </div>
            )}
          </div>
        )}

        <div className="flex items-end">
          <button
            onClick={submitOrder}
            disabled={submitting || !symbol || !qty}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? "Submitting..." : "Submit Order"}
          </button>
        </div>
        {orderResult && (
          <div className={`text-sm px-3 py-2 rounded mt-3 ${orderResult.ok ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
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
            <thead><tr className="text-left text-gray-500"><th>Symbol</th><th>Type</th><th>Side</th><th>Qty</th><th>Price</th><th>Time</th></tr></thead>
            <tbody>
              {trades.map((t, i) => (
                <tr key={i} className="border-t">
                  <td>{String(t.symbol)}</td>
                  <td>{t.asset_type && t.asset_type !== "STK" ? String(t.asset_type) : ""}</td>
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
