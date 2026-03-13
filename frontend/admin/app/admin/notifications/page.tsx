"use client";

import { useEffect, useState } from "react";
import { Bell, Loader2 } from "lucide-react";
import { AdminPageContainer } from "@/components/admin/common/AdminPageContainer";
import { getNotifications } from "@/lib/api";

export default function NotificationsPage() {
    const [notifications, setNotifications] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    async function fetchData() {
        try {
            const data = await getNotifications();
            setNotifications(data);
        } catch (error) {
            console.error("Failed to fetch notifications", error);
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
            <AdminPageContainer title="All Notifications" description="Loading notifications...">
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
                </div>
            </AdminPageContainer>
        )
    }

    return (
        <AdminPageContainer
            title="All Notifications"
            description="View all system alerts and updates"
            icon={<Bell className="w-7 h-7" />}
        >
            <div className="flex flex-col gap-4">
                {notifications.length === 0 ? (
                    <div className="bg-gray-900/50 glass-effect rounded-lg border border-gray-800 p-8 text-center text-gray-500">
                        No new notifications
                    </div>
                ) : (
                    notifications.map((notif, idx) => (
                        <div key={idx} className="bg-gray-900/50 glass-effect rounded-lg border border-gray-800 p-4 hover:bg-gray-800/30 transition-colors flex flex-col gap-2">
                            <div className="flex justify-between items-start">
                                <span className="font-semibold text-white">{notif.title}</span>
                                <span className="text-xs text-gray-500 whitespace-nowrap ml-4">
                                    {new Date(notif.timestamp).toLocaleString()}
                                </span>
                            </div>
                            <p className="text-sm text-gray-400">{notif.message}</p>
                        </div>
                    ))
                )}
            </div>
        </AdminPageContainer>
    );
}
