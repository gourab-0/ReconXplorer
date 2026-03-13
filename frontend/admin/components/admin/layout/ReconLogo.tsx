/**
 * ReconXplorer Logo Component
 * Matches the design of the main dashboard navbar
 */

import Link from "next/link";

export function ReconLogo() {
  return (
    <Link
      href="/admin"
      className="flex items-center gap-3 group cursor-pointer hover:opacity-80 transition-opacity"
    >
      {/* The Icon Box */}
      <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-600 to-blue-900 flex items-center justify-center text-white shadow-lg shadow-blue-500/20 neon-glow-blue">
        <span className="material-symbols-outlined text-[22px]">radar</span>
      </div>

      {/* The Text */}
      <h2 className="text-white text-xl font-black tracking-tight uppercase">
        ReconXplorer
      </h2>
    </Link>
  );
}
