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

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
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
