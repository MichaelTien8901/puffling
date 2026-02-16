"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/backtest", label: "Backtest" },
  { href: "/strategies", label: "Strategies" },
  { href: "/ai", label: "AI Chat" },
  { href: "/data", label: "Data" },
  { href: "/trades", label: "Trades" },
  { href: "/settings", label: "Settings" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <nav className="w-56 bg-gray-900 text-white min-h-screen p-4 flex flex-col gap-1">
      <h1 className="text-xl font-bold mb-6 px-3">Puffling</h1>
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={`px-3 py-2 rounded text-sm ${
            pathname === item.href
              ? "bg-gray-700 text-white"
              : "text-gray-400 hover:text-white hover:bg-gray-800"
          }`}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
