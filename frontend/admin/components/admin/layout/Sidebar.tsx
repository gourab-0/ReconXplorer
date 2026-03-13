/**
 * Admin Sidebar
 * Floating navigation overlay that toggles on/off
 */

"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { X } from "lucide-react";
import {
  LayoutDashboard,
  Users,
  Radar,
  Zap,
  AlertTriangle,
  Activity,
  FileText,
  Settings,
} from "lucide-react";
import { ADMIN_NAV_ITEMS, UI_CONSTANTS } from "@/lib/constants";

const iconMap: Record<string, React.ReactNode> = {
  LayoutDashboard: <LayoutDashboard className="w-5 h-5" />,
  Users: <Users className="w-5 h-5" />,
  Radar: <Radar className="w-5 h-5" />,
  Zap: <Zap className="w-5 h-5" />,
  AlertTriangle: <AlertTriangle className="w-5 h-5" />,
  Activity: <Activity className="w-5 h-5" />,
  FileText: <FileText className="w-5 h-5" />,
  Settings: <Settings className="w-5 h-5" />,
};

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Overlay Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 z-30 backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      {/* Sidebar Overlay */}
      <aside
        className={`fixed left-0 top-16 ${UI_CONSTANTS.SIDEBAR_WIDTH} bg-gray-900/98 glass-effect-md border-r border-gray-800 h-[calc(100vh-64px)] flex flex-col overflow-y-auto z-40 transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Close Button (Mobile) */}
        <div className="flex items-center justify-end p-4 border-b border-gray-800 md:hidden">
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-4 space-y-2">
          {ADMIN_NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            const Icon = iconMap[item.icon as keyof typeof iconMap];

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all ${
                  isActive
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 glow-blue"
                    : "text-gray-400 hover:text-gray-300 hover:bg-gray-800/50 border border-transparent"
                }`}
              >
                {Icon}
                <span className="text-sm font-medium">{item.label}</span>
                {isActive && (
                  <div className="ml-auto w-1 h-4 bg-cyan-400 rounded" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer Info */}
        <div className="p-4 border-t border-gray-800 space-y-2 text-xs text-gray-500">
          <div className="flex items-center justify-between">
            <span>System Status</span>
            <span className="w-2 h-2 bg-emerald-400 rounded-full inline-block" />
          </div>
          <p className="text-gray-600">All systems operational</p>
        </div>
      </aside>
    </>
  );
}
