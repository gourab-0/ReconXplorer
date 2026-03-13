/**
 * Admin Topbar
 * Top navigation bar with menu toggle, search, notifications, and user menu
 */

"use client";

import { Search, Bell, Settings, LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { ReconLogo } from "./ReconLogo";
import { UI_CONSTANTS } from "@/lib/constants";
import { useState, useEffect } from "react";
import { getNotifications, getCurrentUser, signOut } from "@/lib/api";
import Link from "next/link";

interface TopbarProps {
  onMenuClick: () => void;
}

export function Topbar({ onMenuClick }: TopbarProps) {
  const [notifications, setNotifications] = useState<any[]>([]);
  const [user, setUser] = useState<any>(null);

  const handleLogout = async () => {
    try {
        await signOut();
        window.location.href = "http://localhost:3000/login";
    } catch (error) {
        console.error("Logout failed", error);
    }
  };

  useEffect(() => {
    async function fetchData() {
        try {
            const [notifsData, userData] = await Promise.all([
                getNotifications(),
                getCurrentUser()
            ]);
            setNotifications(notifsData);
            setUser(userData);
        } catch (error) {
            console.error("Failed to fetch topbar data", error);
        }
    }
    fetchData();
    const interval = setInterval(fetchData, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  // Calculate initials
  const initials = user?.full_name 
    ? user.full_name.split(" ").map((n: any) => n[0]).join("").substring(0, 2).toUpperCase() 
    : "AD";

  return (
    <header
      className={`${UI_CONSTANTS.TOPBAR_HEIGHT} bg-gray-900/95 glass-effect border-b border-gray-800 fixed top-0 left-0 right-0 z-50`}
    >
      <div className="h-full px-6 flex items-center justify-between gap-4">
        {/* Logo Icon */}
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400"
            title="Toggle Menu"
          >
            <Settings className="w-5 h-5 rotate-90" />
          </button>
          <ReconLogo />
        </div>

        {/* Search Bar */}
        <div className="flex-1 max-w-md hidden md:block">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <Input
              type="text"
              placeholder="Search users, scans, logs..."
              className="pl-10 bg-gray-800/50 border-gray-700 text-gray-300 placeholder:text-gray-600 hover:bg-gray-800 focus:bg-gray-800"
            />
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-4 ml-6">
          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="relative hover:bg-gray-800"
              >
                <Bell className="w-5 h-5 text-gray-400" />
                {notifications.length > 0 && (
                    <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80 bg-gray-900 border-gray-800">
                <DropdownMenuLabel className="text-gray-400">Notifications</DropdownMenuLabel>
                <DropdownMenuSeparator className="bg-gray-800" />
                <div className="max-h-80 overflow-y-auto">
                    {notifications.length === 0 ? (
                        <div className="p-4 text-center text-sm text-gray-500">No new notifications</div>
                    ) : (
                        notifications.map((notif: any, i) => (
                            <DropdownMenuItem key={i} className="flex flex-col items-start gap-1 p-3 hover:bg-gray-800 focus:bg-gray-800 cursor-default">
                                <span className="font-semibold text-white text-sm">{notif.title}</span>
                                <span className="text-xs text-gray-400">
                                    {notif.message.length > 60 ? notif.message.substring(0, 60) + "..." : notif.message}
                                </span>
                                <span className="text-[10px] text-gray-600 self-end">{new Date(notif.timestamp).toLocaleTimeString()}</span>
                            </DropdownMenuItem>
                        ))
                    )}
                </div>
                <DropdownMenuSeparator className="bg-gray-800" />
                <div className="p-2">
                    <Link href="/admin/notifications" className="flex w-full justify-center items-center text-sm font-medium text-cyan-400 hover:text-cyan-300 hover:bg-gray-800 py-2 rounded-md transition-colors">
                        View All Notifications
                    </Link>
                </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="flex items-center gap-2 hover:bg-gray-800"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                  <span className="text-xs font-bold text-white">{initials}</span>
                </div>
                <div className="hidden sm:flex flex-col items-start">
                  <span className="text-sm font-medium text-gray-300">
                    {user?.full_name || "Admin"}
                  </span>
                  <span className="text-xs text-gray-500">{user?.is_admin ? "Super Admin" : "Admin"}</span>
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 bg-gray-900 border-gray-800">
              <Link href="/admin/settings">
                <DropdownMenuItem className="text-gray-300 hover:bg-gray-800 cursor-pointer">
                  <User className="w-4 h-4 mr-2" />
                  Profile
                </DropdownMenuItem>
              </Link>
              <Link href="/admin/settings">
                <DropdownMenuItem className="text-gray-300 hover:bg-gray-800 cursor-pointer">
                  <Settings className="w-4 h-4 mr-2" />
                  Preferences
                </DropdownMenuItem>
              </Link>
              <DropdownMenuSeparator className="bg-gray-800" />
              <DropdownMenuItem 
                className="text-red-400 hover:bg-red-500/10 cursor-pointer"
                onClick={handleLogout}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
