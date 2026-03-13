"use client";

import { useEffect, useState } from "react";
import { FileText, AlertTriangle, AlertCircle, Info, Loader2, Database, ShieldAlert, Users, Server } from "lucide-react";
import { AdminPageContainer } from "@/components/admin/common/AdminPageContainer";
import { getAuditLogs, getSystemHealth, getAllScans, getUsers, getThreatIntelStatus } from "@/lib/api";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function LogsPage() {
  const [loading, setLoading] = useState(true);

  // Data States
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [scans, setScans] = useState<any[]>([]);
  const [healthLogs, setHealthLogs] = useState<any[]>([]);
  const [threatLogs, setThreatLogs] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);

  async function fetchData() {
    try {
      const [auditData, healthData, scansData, usersData, threatData] = await Promise.all([
        getAuditLogs().catch(() => []),
        getSystemHealth().catch(() => []),
        getAllScans().catch(() => []),
        getUsers().catch(() => []),
        getThreatIntelStatus().catch(() => [])
      ]);
      setAuditLogs(auditData || []);
      setHealthLogs(healthData || []);
      setScans(scansData || []);
      setUsers(usersData || []);
      setThreatLogs(threatData || []);
    } catch (error) {
      console.error("Failed to fetch logs data", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <AdminPageContainer title="System Logs" description="Loading comprehensive system logs...">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
        </div>
      </AdminPageContainer>
    )
  }

  return (
    <AdminPageContainer
      title="System Logs"
      description="Comprehensive view of all platform activity and diagnostics"
      icon={<FileText className="w-7 h-7" />}
    >
      <Tabs defaultValue="audit" className="w-full">
        <TabsList className="bg-gray-900/50 border border-gray-800 p-1 mb-6">
          <TabsTrigger value="audit" className="data-[state=active]:bg-gray-800 data-[state=active]:text-cyan-400">
            <FileText className="w-4 h-4 mr-2" />
            Admin Audit
          </TabsTrigger>
          <TabsTrigger value="scans" className="data-[state=active]:bg-gray-800 data-[state=active]:text-cyan-400">
            <ShieldAlert className="w-4 h-4 mr-2" />
            Scan Operations
          </TabsTrigger>
          <TabsTrigger value="system" className="data-[state=active]:bg-gray-800 data-[state=active]:text-cyan-400">
            <Server className="w-4 h-4 mr-2" />
            System Health
          </TabsTrigger>
          <TabsTrigger value="users" className="data-[state=active]:bg-gray-800 data-[state=active]:text-cyan-400">
            <Users className="w-4 h-4 mr-2" />
            Registration Log
          </TabsTrigger>
        </TabsList>

        {/* 1. Admin Audit Logs */}
        <TabsContent value="audit">
          <div className="bg-gray-900/50 glass-effect rounded-lg border border-gray-800 overflow-hidden">
            <div className="overflow-x-auto max-h-[600px]">
              <table className="w-full text-left">
                <thead className="border-b border-gray-800 bg-gray-800/50 sticky top-0">
                  <tr>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Action</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Target</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Details</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">IP Address</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {auditLogs.length === 0 ? (
                    <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">No audit logs found</td></tr>
                  ) : (
                    auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-gray-800/20 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap font-medium text-white">{log.action}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-cyan-400">{log.target_user || "-"}</td>
                        <td className="px-6 py-4 text-gray-400 text-sm">{log.details || "-"}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-gray-500 font-mono text-xs">{log.ip_address || "-"}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-gray-500 text-xs">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        {/* 2. Scan Operations */}
        <TabsContent value="scans">
          <div className="bg-gray-900/50 glass-effect rounded-lg border border-gray-800 overflow-hidden">
            <div className="overflow-x-auto max-h-[600px]">
              <table className="w-full text-left">
                <thead className="border-b border-gray-800 bg-gray-800/50 sticky top-0">
                  <tr>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Target</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Status</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Risk Level</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Details/Error</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Timestamp</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {scans.length === 0 ? (
                    <tr><td colSpan={5} className="px-6 py-8 text-center text-gray-500">No scan history found</td></tr>
                  ) : (
                    scans.map((scan) => (
                      <tr key={scan.id} className="hover:bg-gray-800/20 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap font-medium text-white">{scan.target_value}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 rounded text-xs ${scan.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400' :
                              scan.status === 'failed' ? 'bg-red-500/10 text-red-400' :
                                'bg-amber-500/10 text-amber-400'
                            }`}>
                            {scan.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {scan.risk_level ? (
                            <span className={`text-xs ${scan.risk_level === 'high' || scan.risk_level === 'critical' ? 'text-red-400' :
                                scan.risk_level === 'medium' ? 'text-amber-400' : 'text-emerald-400'
                              }`}>
                              {scan.risk_level.toUpperCase()} ({scan.risk_score || 0})
                            </span>
                          ) : <span className="text-gray-500">-</span>}
                        </td>
                        <td className="px-6 py-4 text-gray-400 text-xs w-1/3">
                          {scan.error ? <span className="text-red-400">{scan.error}</span> : "Scan completed normally"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-gray-500 text-xs">
                          {new Date(scan.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>

        {/* 3. System Health & APIs */}
        <TabsContent value="system">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-900/50 glass-effect rounded-lg border border-gray-800 p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Database className="w-5 h-5" /> Core Infrastructure Logs</h3>
              <div className="space-y-4">
                {healthLogs.map((log, idx) => (
                  <div key={idx} className="flex flex-col gap-1 border-b border-gray-800 pb-3 last:border-0">
                    <div className="flex justify-between">
                      <span className="font-medium text-white">{log.name}</span>
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded ${log.status === 'ok' ? 'bg-emerald-500/10 text-emerald-400' :
                          log.status === 'warning' ? 'bg-amber-500/10 text-amber-400' : 'bg-red-500/10 text-red-400'
                        }`}>
                        {log.status.toUpperCase()}
                      </span>
                    </div>
                    {log.errorMessage && <span className="text-sm text-gray-400">{log.errorMessage}</span>}
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-gray-900/50 glass-effect rounded-lg border border-gray-800 p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2"><Server className="w-5 h-5" /> Provider API Status</h3>
              <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
                {threatLogs.map((api, idx) => (
                  <div key={idx} className="flex justify-between items-center border-b border-gray-800 pb-3 last:border-0">
                    <span className="font-medium text-white">{api.name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${api.status === 'ok' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-gray-800 text-gray-500'
                      }`}>
                      {api.status === 'ok' ? 'CONNECTED' : 'MISSING KEY'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </TabsContent>

        {/* 4. User Registrations */}
        <TabsContent value="users">
          <div className="bg-gray-900/50 glass-effect rounded-lg border border-gray-800 overflow-hidden">
            <div className="overflow-x-auto max-h-[600px]">
              <table className="w-full text-left">
                <thead className="border-b border-gray-800 bg-gray-800/50 sticky top-0">
                  <tr>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">User Name</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Email</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Status</th>
                    <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Registered At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {users.length === 0 ? (
                    <tr><td colSpan={4} className="px-6 py-8 text-center text-gray-500">No users found</td></tr>
                  ) : (
                    users.map((user) => (
                      <tr key={user.id} className="hover:bg-gray-800/20 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap font-medium text-white">{user.full_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-gray-300">{user.email}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 rounded text-xs ${user.is_verified ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                            }`}>
                            {user.is_verified ? 'Verified' : 'Pending'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-gray-500 text-xs">
                          {new Date(user.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </AdminPageContainer>
  );
}
