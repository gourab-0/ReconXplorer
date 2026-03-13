"use client";

import { useEffect, useState } from "react";
import { Users as UsersIcon, MoreVertical, Radar, Check, X, Loader2 } from "lucide-react";
import { AdminPageContainer } from "@/components/admin/common/AdminPageContainer";
import { getUsers, verifyUser, resetUserApiKey, adjustUserLimit, suspendUser, deleteUser } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const data = await getUsers();
      setUsers(data);
    } catch (error) {
      console.error("Failed to fetch users", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  const handleAction = async (action: string, user: any) => {
    const actionLabel = action === 'suspend' 
      ? (user.is_active ? 'suspend' : 'activate') 
      : action.replace('-', ' ');
      
    if (['delete', 'suspend'].includes(action) && !confirm(`Are you sure you want to ${actionLabel} user ${user.email}?`)) return;

    try {
      if (action === 'verify') {
        await verifyUser(user.id);
        alert(`User ${user.email} verified successfully`);
      }
      else if (action === 'reset-api') {
        await resetUserApiKey(user.id);
        alert(`API key for ${user.email} has been reset`);
      }
      else if (action === 'adjust-limit') {
        const newLimit = prompt(`Enter new daily API limit for ${user.full_name}:`, user.api_limit_daily || 10);
        if (newLimit === null) return;
        await adjustUserLimit(user.id, parseInt(newLimit));
        alert(`API limit for ${user.full_name} updated to ${newLimit}`);
      }
      else if (action === 'suspend') {
        await suspendUser(user.id);
        alert(`User ${user.email} ${user.is_active ? 'suspended' : 'activated'} successfully`);
      }
      else if (action === 'delete') {
        await deleteUser(user.id);
        alert(`User ${user.email} and all their data deleted permanently`);
      }
      
      fetchData();
    } catch (error: any) {
      alert(`Failed to ${actionLabel}: ` + (error.response?.data?.detail || "Unknown error"));
    }
  };

  if (loading) {
    return (
        <AdminPageContainer title="User Management" description="Loading users...">
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            </div>
        </AdminPageContainer>
     )
  }

  return (
    <AdminPageContainer
      title="User Management"
      description="View and manage all registered users"
      icon={<UsersIcon className="w-7 h-7" />}
    >
      {/* Users Table */}
      <div className="bg-gray-900/50 glass-effect rounded-lg border border-gray-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-gray-800 bg-gray-800/30">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Organization
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Verified
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  API Usage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {users.map((user) => {
                const limit = user.api_limit_daily || 10;
                const used = user.api_limit_used || 0;
                const usagePercent = (used / limit) * 100;
                const usageColor = usagePercent > 90 ? "text-red-400" : usagePercent > 70 ? "text-amber-400" : "text-emerald-400";
                
                // Initials
                const initials = user.full_name ? user.full_name.split(" ").map((n:any) => n[0]).join("").substring(0,2).toUpperCase() : "U";

                return (
                  <tr key={user.id} className="hover:bg-gray-800/30 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                          <span className="text-xs font-bold text-white">
                            {initials}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-white">{user.full_name}</p>
                          <p className="text-xs text-gray-500">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                      {user.organization || "-"}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-col gap-1">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium w-fit ${
                          user.is_admin
                            ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                            : "bg-gray-700/50 text-gray-300 border border-gray-600/30"
                        }`}>
                          {user.is_admin && <Radar className="w-3 h-3 mr-1" />}
                          {user.is_admin ? "Admin" : "User"}
                        </span>
                        {!user.is_active && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-red-500/20 text-red-400 border border-red-500/30 w-fit uppercase">
                            Suspended
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.is_verified ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400">
                          <Check className="w-4 h-4" />
                          Verified
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-amber-400">
                          <X className="w-4 h-4" />
                          Pending
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-2 bg-gray-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all ${
                              usagePercent > 90
                                ? "bg-red-500"
                                : usagePercent > 70
                                ? "bg-amber-500"
                                : "bg-emerald-500"
                            }`}
                            style={{ width: `${Math.min(usagePercent, 100)}%` }}
                          />
                        </div>
                        <span className={`text-xs font-medium whitespace-nowrap ${usageColor}`}>
                          {usagePercent.toFixed(0)}%
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {used}/{limit}
                      </p>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="bg-gray-900 border-gray-800">
                          <DropdownMenuItem className="text-gray-300 hover:bg-gray-800">
                            View Details
                          </DropdownMenuItem>
                          {!user.is_verified && (
                            <DropdownMenuItem className="text-emerald-400 hover:bg-emerald-500/10" onClick={() => handleAction('verify', user)}>
                              Verify User
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem className="text-gray-300 hover:bg-gray-800" onClick={() => handleAction('reset-api', user)}>
                            Reset API Key
                          </DropdownMenuItem>
                          {user.is_verified && (
                            <DropdownMenuItem className="text-gray-300 hover:bg-gray-800" onClick={() => handleAction('adjust-limit', user)}>
                              Adjust API Limit
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuSeparator className="bg-gray-800" />
                          <DropdownMenuItem 
                            className={user.is_active ? "text-amber-400 hover:bg-amber-500/10" : "text-emerald-400 hover:bg-emerald-500/10"} 
                            onClick={() => handleAction('suspend', user)}
                          >
                            {user.is_active ? "Suspend Account" : "Activate Account"}
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-red-400 hover:bg-red-500/10" onClick={() => handleAction('delete', user)}>
                            Delete User
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
    </AdminPageContainer>
  );
}
