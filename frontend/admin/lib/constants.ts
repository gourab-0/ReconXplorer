/**
 * Admin Panel Constants
 * Color mappings, navigation items, and shared UI configurations
 */

import { ADMIN_ROUTES } from "./admin-routes";

/**
 * Status color mapping for system health components
 * Single source of truth for status visualization
 */
export const STATUS_COLORS = {
  ok: "text-emerald-400 bg-emerald-500/10 border border-emerald-500/30",
  warning:
    "text-amber-400 bg-amber-500/10 border border-amber-500/30",
  error: "text-red-400 bg-red-500/10 border border-red-500/30",
} as const;

/**
 * Risk level color mapping
 * Used across scan results, dashboards, and threat indicators
 */
export const RISK_COLORS = {
  low: "text-emerald-400",
  medium: "text-amber-400",
  high: "text-red-400",
  critical: "text-purple-400",
} as const;

/**
 * Severity color mapping for audit logs
 * Maps audit log severity levels to visual indicators
 */
export const SEVERITY_COLORS = {
  info: "text-blue-400",
  warning: "text-amber-400",
  critical: "text-red-500",
} as const;

/**
 * Admin navigation items for sidebar
 * Defines structure, labels, icons, and routes
 */
export const ADMIN_NAV_ITEMS = [
  {
    label: "Dashboard",
    href: ADMIN_ROUTES.dashboard,
    icon: "LayoutDashboard",
  },
  {
    label: "Users",
    href: ADMIN_ROUTES.users,
    icon: "Users",
  },
  {
    label: "Scans",
    href: ADMIN_ROUTES.scans,
    icon: "Radar",
  },
  {
    label: "API & Limits",
    href: ADMIN_ROUTES.apiLimits,
    icon: "Zap",
  },
  {
    label: "Threat Intel",
    href: ADMIN_ROUTES.threatIntel,
    icon: "AlertTriangle",
  },
  {
    label: "System Health",
    href: ADMIN_ROUTES.system,
    icon: "Activity",
  },
  {
    label: "Logs",
    href: ADMIN_ROUTES.logs,
    icon: "FileText",
  },
  {
    label: "Settings",
    href: ADMIN_ROUTES.settings,
    icon: "Settings",
  },
] as const;

/**
 * Common UI spacing and sizing constants
 */
export const UI_CONSTANTS = {
  SIDEBAR_WIDTH: "w-64",
  TOPBAR_HEIGHT: "h-16",
  CONTENT_MAX_WIDTH: "max-w-7xl",
  PADDING: {
    PAGE: "p-6 md:p-8",
    CARD: "p-4 md:p-6",
    SECTION: "p-4 md:p-5",
  },
  GAP: {
    GRID: "gap-4 md:gap-6",
    STACK: "gap-3 md:gap-4",
  },
} as const;
