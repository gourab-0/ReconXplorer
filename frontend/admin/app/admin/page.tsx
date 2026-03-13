/**
 * Admin Dashboard
 * Main overview page with key metrics and analytics
 */

"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { AlertTriangle, TrendingUp, Users, Zap, Loader2 } from "lucide-react";
import { AdminPageContainer } from "@/components/admin/common/AdminPageContainer";
import { RISK_COLORS } from "@/lib/constants";
import { getAdminStats } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const data = await getAdminStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch admin stats", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
    // Poll every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
     return (
        <AdminPageContainer title="Dashboard" description="Loading system overview...">
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            </div>
        </AdminPageContainer>
     )
  }

  return (
    <AdminPageContainer title="Dashboard" description="System overview and key metrics">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard
          icon={<TrendingUp className="w-6 h-6" />}
          label="Total Scans"
          value={stats?.totalScans?.toLocaleString() || "0"}
          change="Real-time"
          trend="up"
        />
        <StatCard
          icon={<AlertTriangle className="w-6 h-6 text-red-400" />}
          label="Active Threats"
          value={stats?.activeThreats || "0"}
          change="Detected"
          trend="up"
          variant="danger"
        />
        <StatCard
          icon={<TrendingUp className="w-6 h-6 text-amber-400" />}
          label="Avg Risk Score"
          value={stats?.averageRiskScore?.toFixed(1) || "0.0"}
          change="Global Avg"
          trend="stable"
          variant="warning"
        />
        <StatCard
          icon={<Users className="w-6 h-6 text-cyan-400" />}
          label="Total Users"
          value={stats?.totalUsers || "0"}
          change="Registered"
          trend="up"
        />
        <StatCard
          icon={<Zap className="w-6 h-6 text-purple-400" />}
          label="API Calls"
          value={stats?.totalApiCalls?.toLocaleString() || "0"}
          change="Estimated"
          trend="up"
          variant="secondary"
        />
        <StatCard
          icon={<div className="w-6 h-6 text-emerald-400">↑</div>}
          label="Uptime"
          value={`${stats?.uptime || 99.9}%`}
          change="System Healthy"
          trend="stable"
          variant="success"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scans Over Time */}
        <div className="bg-gray-900/50 glass-effect rounded-lg p-6 border border-gray-800">
          <h3 className="text-lg font-semibold text-white mb-4">Scans Over Time</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={stats?.scansOverTime || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip
                contentStyle={{ backgroundColor: "#1F2937", border: "1px solid #374151" }}
                labelStyle={{ color: "#9CA3AF" }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="scans"
                stroke="#06B6D4"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="threats"
                stroke="#EF4444"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Risk Distribution */}
        <div className="bg-gray-900/50 glass-effect rounded-lg p-6 border border-gray-800">
          <h3 className="text-lg font-semibold text-white mb-4">Risk Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={stats?.riskDistribution || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="risk" stroke="#6B7280" />
              <YAxis stroke="#6B7280" />
              <Tooltip
                contentStyle={{ backgroundColor: "#1F2937", border: "1px solid #374151" }}
                labelStyle={{ color: "#9CA3AF" }}
              />
              <Bar dataKey="count" fill="#06B6D4" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Ports Chart */}
      <div className="bg-gray-900/50 glass-effect rounded-lg p-6 border border-gray-800">
        <h3 className="text-lg font-semibold text-white mb-4">Top Scanned Ports</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={stats?.topPorts || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="port" stroke="#6B7280" />
            <YAxis stroke="#6B7280" />
            <Tooltip
              contentStyle={{ backgroundColor: "#1F2937", border: "1px solid #374151" }}
              labelStyle={{ color: "#9CA3AF" }}
            />
            <Bar dataKey="scans" fill="#A855F7" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* High Risk Targets */}
      <div className="bg-gray-900/50 glass-effect rounded-lg p-6 border border-gray-800">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-400" />
          High Risk Targets
        </h3>
        <div className="space-y-3">
          {(stats?.highRiskTargets || []).map((target: any) => (
            <div
              key={target.target}
              className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors"
            >
              <div>
                <p className="font-medium text-white">{target.target}</p>
                <p className="text-xs text-gray-500">
                  {target.scansCount} scans • Last: {new Date(target.lastScanned).toLocaleDateString()}
                </p>
              </div>
              <div className="text-right">
                <div className={`text-lg font-bold ${RISK_COLORS[target.riskLevel as keyof typeof RISK_COLORS] || 'text-red-400'}`}>
                  {target.riskScore}
                </div>
                <span className="text-xs text-gray-400 capitalize">
                  {target.riskLevel}
                </span>
              </div>
            </div>
          ))}
          {(!stats?.highRiskTargets || stats.highRiskTargets.length === 0) && (
            <p className="text-center text-gray-500 py-4 text-sm">No high risk targets detected yet.</p>
          )}
        </div>
      </div>
    </AdminPageContainer>
  );
}

// Stat Card Component
interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  change: string;
  trend: "up" | "down" | "stable";
  variant?: "default" | "danger" | "warning" | "secondary" | "success";
}

function StatCard({
  icon,
  label,
  value,
  change,
  trend,
  variant = "default",
}: StatCardProps) {
  const variantStyles = {
    default: "border-cyan-500/30 bg-cyan-500/5",
    danger: "border-red-500/30 bg-red-500/5",
    warning: "border-amber-500/30 bg-amber-500/5",
    secondary: "border-purple-500/30 bg-purple-500/5",
    success: "border-emerald-500/30 bg-emerald-500/5",
  };

  return (
    <div
      className={`p-6 rounded-lg border glass-effect transition-all hover:scale-105 ${variantStyles[variant]}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="text-gray-400">{icon}</div>
        <span className={`text-xs font-semibold ${
          trend === "up" ? "text-red-400" : trend === "down" ? "text-emerald-400" : "text-gray-400"
        }`}>
          {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} {change}
        </span>
      </div>
      <h3 className="text-sm font-medium text-gray-400 mb-1">{label}</h3>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}
