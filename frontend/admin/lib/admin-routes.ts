/**
 * Admin Panel Routes
 * Centralized constant for all admin navigation paths
 * Prevents typo bugs and enables safe route refactoring
 */

export const ADMIN_ROUTES = {
  dashboard: "/admin",
  users: "/admin/users",
  scans: "/admin/scans",
  apiLimits: "/admin/api-limits",
  threatIntel: "/admin/threat-intel",
  system: "/admin/system-health",
  logs: "/admin/logs",
  settings: "/admin/settings",
} as const;

export type AdminRoute = (typeof ADMIN_ROUTES)[keyof typeof ADMIN_ROUTES];
