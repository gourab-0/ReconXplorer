/**
 * Admin Layout
 * Main wrapper component for all admin pages
 */

"use client";

import { ReactNode, useState } from "react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { UI_CONSTANTS } from "@/lib/constants";

interface AdminLayoutProps {
  children: ReactNode;
}

export function AdminLayout({ children }: AdminLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="bg-black/95 grid-background min-h-screen">
      {/* Fixed Topbar */}
      <Topbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

      {/* Floating Sidebar Overlay */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Page Content with top padding to account for fixed header */}
      <div className="pt-16 min-h-screen">
        <div className="bg-gradient-to-b from-gray-900/50 to-black/80 min-h-full">
          {children}
        </div>
      </div>
    </div>
  );
}
