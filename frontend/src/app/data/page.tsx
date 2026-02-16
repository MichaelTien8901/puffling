"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import Chart from "@/components/Chart";
import { CandlestickData } from "lightweight-charts";

export default function DataPage() {
  const [symbol, setSymbol] = useState("AAPL");
  const [start, setStart] = useState("2024-01-01");
  const [end, setEnd] = useState("2024-12-31");
  const [chartData, setChartData] = useState<CandlestickData[]>([]);

  const fetchData = async () => {
    const res = await api.get<{ data: Record<string, unknown>[] }>(
      `/api/data/ohlcv?symbol=${symbol}&start=${start}&end=${end}`
    );
    const mapped = res.data.map((d) => ({
      time: String(d.Date || d.index).split("T")[0],
      open: Number(d.Open),
      high: Number(d.High),
      low: Number(d.Low),
      close: Number(d.Close),
    })) as CandlestickData[];
    setChartData(mapped);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Data Explorer</h1>
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-3 mb-4">
          <input className="border rounded px-3 py-2" placeholder="Symbol" value={symbol} onChange={(e) => setSymbol(e.target.value)} />
          <input type="date" className="border rounded px-3 py-2" value={start} onChange={(e) => setStart(e.target.value)} />
          <input type="date" className="border rounded px-3 py-2" value={end} onChange={(e) => setEnd(e.target.value)} />
          <button onClick={fetchData} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Load</button>
        </div>
        {chartData.length > 0 && <Chart type="candlestick" data={chartData} />}
      </div>
    </div>
  );
}
