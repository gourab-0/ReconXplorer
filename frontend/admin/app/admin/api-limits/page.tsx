"use client";

import { useEffect, useState } from "react";
import { Zap, Settings, AlertCircle, MoreVertical, Loader2 } from "lucide-react";
import { AdminPageContainer } from "@/components/admin/common/AdminPageContainer";
import { getUsers, resetAllApiUsage, updateDefaultApiLimit, adjustUserLimit } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export default function ApiLimitsPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [defaultLimit, setDefaultLimit] = useState(10);

  const fetchData = async () => {
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (error) {
      console.error("Failed to fetch users for API limits", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleResetAll = async () => {
    if (!confirm("Are you sure you want to reset ALL user API counters? This cannot be undone.")) return;
    try {
      await resetAllApiUsage();
      alert("All counters reset successfully");
      fetchData();
    } catch (error: any) {
      const detail = error.response?.data?.detail || "Unknown error";
      alert(`Failed to reset counters: ${detail}`);
    }
  };

  const handleUpdateDefaultLimit = async () => {
    try {
      await updateDefaultApiLimit(defaultLimit);
      alert("Default limit updated successfully");
    } catch (error) {
      alert("Failed to update default limit");
    }
  };

  const handleEditUserLimit = async (user: any) => {
    const newLimit = prompt(`Enter new daily API limit for ${user.full_name}:`, user.api_limit_daily || 10);
    if (newLimit === null) return;
    try {
      await adjustUserLimit(user.id, parseInt(newLimit));
      alert("User limit updated");
      fetchData();
    } catch (error) {
      alert("Failed to update user limit");
    }
  };

  if (loading) {
    return (
        <AdminPageContainer title="API & Rate Limits" description="Loading usage data...">
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            </div>
        </AdminPageContainer>
     )
  }

  return (
    <AdminPageContainer
      title="API & Rate Limits"
      description="Manage API usage and rate limiting for users"
      icon={<Zap className="w-7 h-7" />}
    >
      {/* Global Limits Section */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          <Settings className="w-5 h-5 text-cyan-400" />
          Global Configuration
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Default API Limit */}
          <div className="bg-gray-900/50 glass-effect rounded-lg p-6 border border-gray-800">
            <label className="text-sm font-medium text-gray-300 mb-2 block">
              Default Daily API Calls
            </label>
            <div className="flex gap-2">
              <Input
                type="number"
                value={defaultLimit}
                onChange={(e) => setDefaultLimit(parseInt(e.target.value))}
                className="flex-1 bg-gray-800 border-gray-700 text-white"
              />
              <Button 
                variant="outline" 
                className="px-6 border-gray-700 hover:bg-gray-800"
                onClick={handleUpdateDefaultLimit}
              >
                Update
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Current default limit per user per day
            </p>
          </div>

          <div className="bg-gray-900/50 glass-effect rounded-lg p-6 border border-gray-800 flex flex-col justify-center">
            <p className="text-sm text-gray-400 mb-4">
              Reset all API call counters for the day manually
            </p>
            <Button
              variant="destructive"
              className="w-full bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20"
              onClick={handleResetAll}
            >
              Emergency Reset Counters
            </Button>
          </div>
        </div>
      </div>

      {/* User Usage Section */}
      <div className="space-y-4 mt-8">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-purple-400" />
          User Resource Usage
        </h2>

        <div className="bg-gray-900/50 glass-effect rounded-lg border border-gray-800 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead className="border-b border-gray-800 bg-gray-800/30">
                <tr>
                  <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">User</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Used</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Limit</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase">Usage %</th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-400 uppercase text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {users.map((user) => {
                  const limit = user.api_limit_daily || 10;
                  const used = user.api_limit_used || 0;
                  const percentage = (used / limit) * 100;
                  const usageColor =
                    percentage > 90
                      ? "text-red-400"
                      : percentage > 70
                      ? "text-amber-400"
                      : "text-emerald-400";

                  return (
                    <tr key={user.id} className="hover:bg-gray-800/30">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <p className="text-sm font-medium text-white">{user.full_name}</p>
                          <p className="text-xs text-gray-500">{user.email}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        {used}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                        {limit}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                percentage > 90
                                  ? "bg-red-500"
                                  : percentage > 70
                                  ? "bg-amber-500"
                                  : "bg-emerald-500"
                              }`}
                              style={{ width: `${Math.min(percentage, 100)}%` }}
                            />
                          </div>
                          <span className={`text-xs font-medium ${usageColor}`}>
                            {percentage.toFixed(0)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="text-gray-400 hover:text-white"
                          onClick={() => handleEditUserLimit(user)}
                        >
                          Edit
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AdminPageContainer>
  );
}
