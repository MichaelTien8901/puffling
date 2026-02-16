"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface Job {
  id: number;
  job_type: string;
  schedule: string;
  config: string;
  enabled: boolean;
}

const JOB_TYPES = ["market_scan", "portfolio_check", "ai_analysis", "alert_check"];

export default function SchedulerPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobType, setJobType] = useState("market_scan");
  const [schedule, setSchedule] = useState("0 9 * * 1-5");
  const [config, setConfig] = useState('{"strategy_type":"momentum","symbols":["SPY"]}');

  const load = () => api.get<Job[]>("/api/scheduler/").then(setJobs).catch(() => {});
  useEffect(() => { load(); }, []);

  const create = async () => {
    let parsed: Record<string, unknown>;
    try { parsed = JSON.parse(config); } catch { return; }
    await api.post("/api/scheduler/", { job_type: jobType, schedule, config: parsed });
    setConfig('{}');
    load();
  };

  const toggle = async (id: number, enabled: boolean) => {
    await api.put(`/api/scheduler/${id}`, { enabled: !enabled });
    load();
  };

  const remove = async (id: number) => {
    await api.delete(`/api/scheduler/${id}`);
    load();
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Scheduler</h1>

      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">New Job</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Job Type</label>
            <select className="border rounded px-3 py-2 w-full" value={jobType} onChange={(e) => setJobType(e.target.value)}>
              {JOB_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Schedule (cron)</label>
            <input className="border rounded px-3 py-2 w-full" value={schedule} onChange={(e) => setSchedule(e.target.value)} placeholder="0 9 * * 1-5" />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-1">Config (JSON)</label>
            <input className="border rounded px-3 py-2 w-full font-mono text-sm" value={config} onChange={(e) => setConfig(e.target.value)} />
          </div>
        </div>
        <button onClick={create} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Create Job</button>
      </div>

      <div className="bg-white rounded-lg shadow p-4">
        <h2 className="text-lg font-semibold mb-3">Scheduled Jobs</h2>
        {jobs.length === 0 ? (
          <p className="text-gray-500">No scheduled jobs</p>
        ) : (
          <table className="w-full text-sm">
            <thead><tr className="text-left text-gray-500"><th>Type</th><th>Schedule</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.id} className="border-t">
                  <td className="py-2">{j.job_type}</td>
                  <td className="font-mono text-xs">{j.schedule}</td>
                  <td>
                    <button onClick={() => toggle(j.id, j.enabled)} className={`px-2 py-0.5 rounded text-xs ${j.enabled ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                      {j.enabled ? "Enabled" : "Disabled"}
                    </button>
                  </td>
                  <td><button onClick={() => remove(j.id)} className="text-red-500 text-sm">Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
