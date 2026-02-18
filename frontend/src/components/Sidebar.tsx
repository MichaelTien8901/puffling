"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/backtest", label: "Backtest" },
  { href: "/optimize", label: "Optimize" },
  { href: "/strategies", label: "Strategies" },
  { href: "/ai", label: "AI Chat" },
  { href: "/agent", label: "Agent" },
  { href: "/data", label: "Data" },
  { href: "/trades", label: "Trades" },
  { href: "/portfolio", label: "Portfolio" },
  { href: "/risk", label: "Risk" },
  { href: "/scheduler", label: "Scheduler" },
  { href: "/settings", label: "Settings" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <nav className="w-56 bg-gray-900 text-white min-h-screen p-4 flex flex-col gap-1">
      <div className="mb-6 px-3">
        <Image src="/puffling_logo.png" alt="Puffling" width={200} height={105} priority />
      </div>
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
