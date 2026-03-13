"use client";

import { useEffect, useState } from "react";
import { Activity, CheckCircle, AlertCircle, XCircle, RefreshCw, Loader2 } from "lucide-react";
import { AdminPageContainer } from "@/components/admin/common/AdminPageContainer";
import { getSystemHealth } from "@/lib/api";
import { Button } from "@/components/ui/button";

export default function SystemHealthPage() {
  const [healthData, setHealthData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function fetchData() {
    try {
      const data = await getSystemHealth();
      setHealthData(data);
    } catch (error) {
      console.error("Failed to fetch system health", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const statusIcons = {
    ok: <CheckCircle className="w-6 h-6 text-emerald-400" />,
    warning: <AlertCircle className="w-6 h-6 text-amber-400" />,
    error: <XCircle className="w-6 h-6 text-red-400" />,
  };

  const statusLabels = {
    ok: "Operational",
    warning: "Warning",
    error: "Down",
  };

  const statusColors = {
    ok: "border-emerald-500/30 bg-emerald-500/5",
    warning: "border-amber-500/30 bg-amber-500/5",
    error: "border-red-500/30 bg-red-500/5",
  };

  if (loading) {
    return (
        <AdminPageContainer title="System Health" description="Loading component status...">
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            </div>
        </AdminPageContainer>
     )
  }

  return (
    <AdminPageContainer
      title="System Health"
      description="Monitor the status of all system components"
      icon={<Activity className="w-7 h-7" />}
    >
      {/* Health Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {healthData.map((service) => (
          <div
            key={service.name}
            className={`rounded-lg p-6 border glass-effect transition-all hover:scale-105 ${
              statusColors[service.status as keyof typeof statusColors] || statusColors.error
            }`}
          >
            {/* Header with Icon and Status */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                {statusIcons[service.status as keyof typeof statusIcons] || statusIcons.error}
                <div>
                  <h3 className="font-semibold text-white">{service.name}</h3>
                  <p className={`text-xs font-medium mt-1 ${
                    service.status === "ok"
                      ? "text-emerald-400"
                      : service.status === "warning"
                      ? "text-amber-400"
                      : "text-red-400"
                  }`}>
                    {statusLabels[service.status as keyof typeof statusLabels] || "Unknown"}
                  </p>
                </div>
              </div>
            </div>

            {/* Last Checked */}
            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-1">Last Checked</p>
              <p className="text-sm text-gray-300">
                {service.lastChecked}
              </p>
            </div>

            {/* Error Message (if any) */}
            {service.errorMessage && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded">
                <p className="text-xs text-red-300">{service.errorMessage}</p>
              </div>
            )}

            {/* Check Status Button */}
            <Button
              variant="outline"
              size="sm"
              className="w-full text-xs border-gray-700 hover:bg-gray-800"
              onClick={() => fetchData()}
            >
              <RefreshCw className="w-3 h-3 mr-2" />
              Check Now
            </Button>
          </div>
        ))}
      </div>
    </AdminPageContainer>
  );
}
