/**
 * Data for Admin Panel
 * Initialized with empty values
 */

import {
  AdminUser,
  AdminScan,
  SystemHealth,
  ApiUsage,
  AuditLog,
  ThreatIntelService,
  HighRiskTarget,
  DashboardStats,
} from "@/types/admin";

export const mockDashboardStats: DashboardStats = {
  totalScans: 0,
  activeThreats: 0,
  averageRiskScore: 0,
  totalUsers: 0,
  totalApiCalls: 0,
  uptime: 100,
};

export const mockUsers: AdminUser[] = [];

export const mockScans: AdminScan[] = [];

export const mockHighRiskTargets: HighRiskTarget[] = [];

export const mockSystemHealth: SystemHealth[] = [
  {
    name: "Database",
    status: "ok",
    lastChecked: new Date(),
  },
  {
    name: "Nmap Service",
    status: "ok",
    lastChecked: new Date(),
  },
  {
    name: "WhatWeb Scanner",
    status: "ok",
    lastChecked: new Date(),
  },
  {
    name: "Gemini API",
    status: "ok",
    lastChecked: new Date(),
  },
  {
    name: "Threat Intelligence",
    status: "ok",
    lastChecked: new Date(),
  },
  {
    name: "Email Service",
    status: "ok",
    lastChecked: new Date(),
  },
];

export const mockThreatIntel: ThreatIntelService[] = [];

export const mockAuditLogs: AuditLog[] = [];

export const mockApiUsageByUser: ApiUsage[] = [];

/**
 * Chart data for dashboard visualizations
 */
export const mockScansOverTimeData: any[] = [];

export const mockRiskDistributionData = [
  { risk: "Low", count: 0 },
  { risk: "Medium", count: 0 },
  { risk: "High", count: 0 },
  { risk: "Critical", count: 0 },
];

export const mockTopPortsData: any[] = [];
