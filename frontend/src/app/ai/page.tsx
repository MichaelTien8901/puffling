"use client";

import { useState, useEffect, useRef } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function AIPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const { lastMessage, isConnected, send } = useWebSocket("/ws/ai/chat");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!lastMessage) return;
    const data = JSON.parse(lastMessage);
    if (data.type === "start") {
      setStreaming(true);
    } else if (data.type === "token") {
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.role === "assistant") {
          return [...prev.slice(0, -1), { ...last, content: last.content + data.content }];
        }
        return [...prev, { role: "assistant", content: data.content }];
      });
    } else if (data.type === "end") {
      setStreaming(false);
    } else if (data.type === "error") {
      setMessages((prev) => [...prev, { role: "assistant", content: `Error: ${data.content}` }]);
      setStreaming(false);
    }
  }, [lastMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || !isConnected) return;
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    send({ message: input });
    setInput("");
  };

  return (
    <div className="flex flex-col h-[calc(100vh-3rem)]">
      <h1 className="text-2xl font-bold mb-4">AI Trading Assistant</h1>
      <div className="flex-1 bg-white rounded-lg shadow p-4 overflow-y-auto mb-4">
        {messages.length === 0 && <p className="text-gray-400">Ask me about markets, strategies, or trading...</p>}
        {messages.map((m, i) => (
          <div key={i} className={`mb-3 ${m.role === "user" ? "text-right" : ""}`}>
            <div className={`inline-block px-3 py-2 rounded-lg text-sm max-w-[80%] ${m.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-800"}`}>
              {m.content}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded px-3 py-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={isConnected ? "Type a message..." : "Connecting..."}
          disabled={!isConnected || streaming}
        />
        <button onClick={handleSend} disabled={!isConnected || streaming} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50">
          Send
        </button>
      </div>
    </div>
  );
}
