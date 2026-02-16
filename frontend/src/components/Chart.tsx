"use client";

import { useEffect, useRef } from "react";
import { createChart, IChartApi, ISeriesApi, CandlestickData, LineData, CandlestickSeries, LineSeries } from "lightweight-charts";

interface ChartProps {
  type?: "candlestick" | "line";
  data: CandlestickData[] | LineData[];
  width?: number;
  height?: number;
}

export default function Chart({ type = "candlestick", data, height = 400 }: ChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | ISeriesApi<"Line"> | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      height,
      layout: { background: { color: "#ffffff" }, textColor: "#333" },
      grid: { vertLines: { color: "#f0f0f0" }, horzLines: { color: "#f0f0f0" } },
      crosshair: { mode: 0 },
      timeScale: { borderColor: "#d1d5db" },
    });
    chartRef.current = chart;

    if (type === "candlestick") {
      const series = chart.addSeries(CandlestickSeries);
      series.setData(data as CandlestickData[]);
      seriesRef.current = series;
    } else {
      const series = chart.addSeries(LineSeries, { color: "#2563eb" });
      series.setData(data as LineData[]);
      seriesRef.current = series;
    }

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);
    handleResize();

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [type, data, height]);

  return <div ref={containerRef} className="w-full" />;
}
