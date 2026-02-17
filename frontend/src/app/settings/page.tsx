"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, unknown>>({});
  const [key, setKey] = useState("");
  const [value, setValue] = useState("");

  const load = () => api.get<Record<string, unknown>>("/api/settings/").then(setSettings).catch(() => {});

  useEffect(() => { load(); }, []);

  const save = async () => {
    if (!key) return;
    let parsed: unknown;
    try { parsed = JSON.parse(value); } catch { parsed = value; }
    await api.put("/api/settings/", { key, value: parsed });
    setKey("");
    setValue("");
    load();
  };

  const remove = async (k: string) => {
    await api.delete(`/api/settings/${k}`);
    load();
  };

  const [safety, setSafety] = useState<Record<string, unknown>>({});

  const loadSafety = () => api.get<Record<string, unknown>>("/api/safety/").then(setSafety).catch(() => {});

  useEffect(() => { loadSafety(); }, []);

  const toggleKillSwitch = async () => {
    if (safety.kill_switch) {
      await api.post("/api/safety/resume", {});
    } else {
      await api.post("/api/safety/kill", {});
    }
    loadSafety();
  };

  const updateSafety = async (field: string, value: unknown) => {
    await api.put("/api/safety/", { [field]: value });
    loadSafety();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      {/* Safety Controls */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">Safety Controls</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium">Kill Switch</span>
              <p className="text-sm text-gray-500">Immediately halt all autonomous trading</p>
            </div>
            <button onClick={toggleKillSwitch} className={`px-4 py-2 rounded font-medium ${safety.kill_switch ? "bg-green-600 text-white hover:bg-green-700" : "bg-red-600 text-white hover:bg-red-700"}`}>
              {safety.kill_switch ? "Resume Trading" : "KILL SWITCH"}
            </button>
          </div>
          {!!safety.kill_switch && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
              All autonomous trading is currently halted.
            </div>
          )}
          <div className="flex items-center justify-between">
            <span>Paper Trading</span>
            <span className={`px-2 py-1 rounded text-sm ${safety.paper_trading ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
              {safety.paper_trading ? "ON" : "OFF"}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span>Max Daily Trades</span>
            <input type="number" className="border rounded px-2 py-1 w-20 text-right" value={String(safety.max_daily_trades || 10)} onChange={(e) => updateSafety("max_daily_trades", parseInt(e.target.value))} />
          </div>
          <div className="flex items-center justify-between">
            <span>Max Position Size (%)</span>
            <input type="number" className="border rounded px-2 py-1 w-20 text-right" value={String((Number(safety.max_position_pct) || 0.1) * 100)} onChange={(e) => updateSafety("max_position_pct", parseFloat(e.target.value) / 100)} />
          </div>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">Add Setting</h2>
        <div className="flex gap-3">
          <input className="border rounded px-3 py-2" placeholder="Key" value={key} onChange={(e) => setKey(e.target.value)} />
          <input className="border rounded px-3 py-2 flex-1" placeholder="Value (JSON or string)" value={value} onChange={(e) => setValue(e.target.value)} />
          <button onClick={save} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Save</button>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-3">Current Settings</h2>
        {Object.keys(settings).length === 0 ? (
          <p className="text-gray-500">No settings configured</p>
        ) : (
          <table className="w-full text-sm">
            <thead><tr className="text-left text-gray-500"><th>Key</th><th>Value</th><th></th></tr></thead>
            <tbody>
              {Object.entries(settings).map(([k, v]) => (
                <tr key={k} className="border-t">
                  <td className="font-mono">{k}</td>
                  <td>{JSON.stringify(v)}</td>
                  <td><button onClick={() => remove(k)} className="text-red-500 text-sm">Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
