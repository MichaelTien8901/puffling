"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useWebSocket } from "@/hooks/useWebSocket";

interface AgentLog {
  id: number;
  run_at: string;
  report: string;
  actions_taken: string;
}

export default function AgentPage() {
  const [logs, setLogs] = useState<AgentLog[]>([]);
  const [running, setRunning] = useState(false);
  const [activity, setActivity] = useState<string[]>([]);
  const { lastMessage } = useWebSocket("/ws/agent");

  useEffect(() => {
    api.get<AgentLog[]>("/api/agent/logs").then(setLogs).catch(() => {});
  }, []);

  useEffect(() => {
    if (lastMessage) {
      setActivity((prev) => [...prev, lastMessage].slice(-50));
    }
  }, [lastMessage]);

  const runAgent = async () => {
    setRunning(true);
    setActivity([]);
    try {
      await api.post("/api/agent/run", { max_api_calls: 10 });
      api.get<AgentLog[]>("/api/agent/logs").then(setLogs).catch(() => {});
    } catch (e) {
      console.error(e);
    }
    setRunning(false);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">AI Agent Activity</h1>
        <button onClick={runAgent} disabled={running} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50">
          {running ? "Running..." : "Run Agent Now"}
        </button>
      </div>

      {activity.length > 0 && (
        <div className="bg-gray-900 text-green-400 rounded-lg p-4 mb-6 font-mono text-sm max-h-48 overflow-y-auto">
          {activity.map((a, i) => (
            <div key={i}>{a}</div>
          ))}
        </div>
      )}

      <div className="space-y-4">
        {logs.length === 0 ? (
          <p className="text-gray-500">No agent runs yet. Click &quot;Run Agent Now&quot; to start.</p>
        ) : (
          logs.map((log) => {
            let report: Record<string, unknown> = {};
            try { report = JSON.parse(log.report); } catch {}
            return (
              <div key={log.id} className="bg-white rounded-lg shadow p-4">
                <div className="flex justify-between mb-2">
                  <span className="font-semibold">Run #{log.id}</span>
                  <span className="text-sm text-gray-500">{log.run_at}</span>
                </div>
                <div className="text-sm mb-2">{String(report.analysis || "No analysis available")}</div>
                {Array.isArray(report.suggestions) && report.suggestions.length > 0 && (
                  <div className="text-sm text-yellow-700 bg-yellow-50 p-2 rounded">
                    Suggestions: {JSON.stringify(report.suggestions)}
                  </div>
                )}
                {Array.isArray(report.actions_taken) && report.actions_taken.length > 0 && (
                  <div className="text-sm text-green-700 bg-green-50 p-2 rounded mt-1">
                    Actions: {JSON.stringify(report.actions_taken)}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
