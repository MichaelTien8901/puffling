"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface StrategyConfig {
  id: number;
  name: string;
  strategy_type: string;
  params: string;
}

export default function StrategiesPage() {
  const [configs, setConfigs] = useState<StrategyConfig[]>([]);
  const [name, setName] = useState("");
  const [strategyType, setStrategyType] = useState("momentum");

  const load = () => api.get<StrategyConfig[]>("/api/strategies/").then(setConfigs).catch(() => {});

  useEffect(() => { load(); }, []);

  const create = async () => {
    await api.post("/api/strategies/", { name, strategy_type: strategyType, params: {} });
    setName("");
    load();
  };

  const remove = async (id: number) => {
    await api.delete(`/api/strategies/${id}`);
    load();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Strategies</h1>
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">New Strategy</h2>
        <div className="flex gap-3">
          <input className="border rounded px-3 py-2" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <input className="border rounded px-3 py-2" placeholder="Type" value={strategyType} onChange={(e) => setStrategyType(e.target.value)} />
          <button onClick={create} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Create</button>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-3">Saved Strategies</h2>
        {configs.length === 0 ? (
          <p className="text-gray-500">No strategies configured</p>
        ) : (
          <table className="w-full text-sm">
            <thead><tr className="text-left text-gray-500"><th>Name</th><th>Type</th><th></th></tr></thead>
            <tbody>
              {configs.map((c) => (
                <tr key={c.id} className="border-t">
                  <td>{c.name}</td>
                  <td>{c.strategy_type}</td>
                  <td><button onClick={() => remove(c.id)} className="text-red-500 text-sm">Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
