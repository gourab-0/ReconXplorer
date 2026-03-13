/**
 * Admin Panel Type Definitions
 * Central source of truth for all admin interface types
 */

export type Status = "ok" | "warning" | "error";
export type Severity = "info" | "warning" | "critical";
export type RiskLevel = "low" | "medium" | "high" | "critical";
export type ScanStatus = "completed" | "in_progress" | "failed" | "pending";

export interface AdminUser {
  id: string;
  email: string;
  name: string;
  organization: string;
  verified: boolean;
  role: "admin" | "user";
  apiUsage: {
    used: number;
    limit: number;
  };
  createdAt: Date;
  lastLogin?: Date;
}

export interface AdminScan {
  id: string;
  target: string;
  riskScore: number;
  riskLevel: RiskLevel;
  status: ScanStatus;
  timestamp: Date;
  userId: string;
  userName: string;
  findings?: number;
  duration?: number;
}

export interface SystemHealth {
  name: string;
  status: Status;
  lastChecked: Date;
  details?: string;
  errorMessage?: string;
}

export interface ApiUsage {
  userId: string;
  userName: string;
  used: number;
  limit: number;
  percentage: number;
  lastReset: Date;
}

export interface AuditLog {
  id: string;
  action: string;
  user: string;
  userId: string;
  timestamp: Date;
  severity: Severity;
  details: string;
  ipAddress?: string;
}

export interface ThreatIntelService {
  id: string;
  name: string;
  status: Status;
  apiKeyMasked: string; // Format: ••••••••••
  lastCheck?: Date;
  errorMessage?: string;
  enabled: boolean;
}

export interface HighRiskTarget {
  target: string;
  riskScore: number;
  riskLevel: RiskLevel;
  scansCount: number;
  lastScanned: Date;
}

export interface DashboardStats {
  totalScans: number;
  activeThreats: number;
  averageRiskScore: number;
  totalUsers: number;
  totalApiCalls: number;
  uptime: number; // percentage
}
