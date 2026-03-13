"use client";

import { useEffect, useState } from "react";
import {
  Radar,
  MoreVertical,
  Play,
  Eye,
  Trash2,
  Zap,
  Clock,
  Loader2,
  FileSearch,
} from "lucide-react";
import { AdminPageContainer } from "@/components/admin/common/AdminPageContainer";
import { getAllScans, deleteScan } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { RISK_COLORS } from "@/lib/constants";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { ScanDetailsModal } from "@/components/admin/scans/ScanDetailsModal";

export default function ScansPage() {
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedScan, setSelectedScan] = useState<any>(null);

  async function fetchData() {
    try {
      const data = await getAllScans();
      setScans(data);
    } catch (error) {
      console.error("Failed to fetch scans", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  const handleAction = async (action: string, scan: any) => {
    if (action === 'view') {
        setSelectedScan(scan);
    } else if (action === 'delete') {
        if (confirm(`Are you sure you want to permanently purge the scan for ${scan.target_value}?`)) {
            try {
                await deleteScan(scan.id);
                alert("Scan artifact purged successfully.");
                fetchData();
            } catch (error: any) {
                alert("Failed to purge scan: " + (error.response?.data?.detail || "Unknown error"));
            }
        }
    }
  };

  if (loading) {
    return (
        <AdminPageContainer title="Scans Management" description="Loading scans...">
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            </div>
        </AdminPageContainer>
     )
  }

  return (
    <AdminPageContainer
      title="Scans Management"
      description="View and manage security scans"
      icon={<Radar className="w-7 h-7" />}
    >
      {/* Scans Table */}
      <div className="bg-gray-900/50 glass-effect rounded-lg border border-gray-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-gray-800 bg-gray-800/30">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Target
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Risk Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Findings
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {scans.map((scan) => {
                const statusColors = {
                  completed: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
                  running: "bg-blue-500/20 text-blue-300 border-blue-500/30 animate-pulse",
                  failed: "bg-red-500/20 text-red-300 border-red-500/30",
                  pending: "bg-gray-500/20 text-gray-300 border-gray-500/30",
                };

                return (
                  <tr key={scan.id} className="hover:bg-gray-800/30 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <p className="text-sm font-medium text-white font-mono">
                        {scan.target_value || scan.target}
                      </p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className={`font-bold ${RISK_COLORS[scan.risk_level as keyof typeof RISK_COLORS] || 'text-gray-400'}`}>
                          {scan.risk_score || "0"}
                        </div>
                        <span className={`text-xs capitalize ${RISK_COLORS[scan.risk_level as keyof typeof RISK_COLORS] || 'text-gray-400'}`}>
                          {scan.risk_level || "pending"}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                          statusColors[scan.status as keyof typeof statusColors] || statusColors.pending
                        }`}
                      >
                        {scan.status === "running" && (
                          <Clock className="w-3 h-3 mr-1 animate-spin" />
                        )}
                        {scan.status?.replace("_", " ") || "unknown"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-300">
                          {scan.findings_count || "0"} found
                        </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {new Date(scan.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="bg-gray-900 border-gray-800">
                          <DropdownMenuItem className="text-gray-300 hover:bg-gray-800" onClick={() => handleAction('view', scan)}>
                            <Eye className="w-4 h-4 mr-2" />
                            View Artifact
                          </DropdownMenuItem>
                          <DropdownMenuSeparator className="bg-gray-800" />
                          <DropdownMenuItem className="text-red-400 hover:bg-red-500/10" onClick={() => handleAction('delete', scan)}>
                            <Trash2 className="w-4 h-4 mr-2" />
                            Purge Artifact
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
      
      {selectedScan && (
        <ScanDetailsModal 
            scan={selectedScan} 
            onClose={() => setSelectedScan(null)} 
        />
      )}
    </AdminPageContainer>
  );
}
