import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

// Helper to get CSRF token from cookies
function getCsrfToken() {
    if (typeof document === 'undefined') return null;
    return document.cookie
      .split('; ')
      .find(row => row.startsWith('csrf_token='))
      ?.split('=')[1];
}

// Add CSRF token to all non-GET requests
api.interceptors.request.use((config) => {
    if (config.method && config.method.toLowerCase() !== 'get') {
        const token = getCsrfToken();
        if (token) {
            config.headers['X-CSRF-Token'] = token;
        }
    }
    return config;
});

export const getAdminStats = async () => {
  const response = await api.get("/admin/stats");
  return response.data;
};

export const getUsers = async () => {
  const response = await api.get("/admin/users");
  return response.data;
};

export const getCurrentUser = async () => {
    const response = await api.get("/auth/me");
    return response.data;
};

export const signOut = async () => {
    await api.post("/auth/logout");
};

export const getSystemHealth = async () => {
  const response = await api.get("/admin/health");
  return response.data;
};

export const getThreatIntelStatus = async () => {
  const response = await api.get("/admin/threat-intel");
  return response.data;
};

export const getAllScans = async () => {
    const response = await api.get("/admin/scans");
    return response.data;
};

export const getNotifications = async () => {
    try {
        const response = await api.get("/admin/notifications");
        return response.data;
    } catch {
        return [];
    }
};

export const getAuditLogs = async () => {
    const response = await api.get("/admin/audit-logs");
    return response.data;
};

// Admin Management Actions
export const resetAllApiUsage = async () => {
    const response = await api.post("/admin/config/reset-api-usage");
    return response.data;
};

export const updateDefaultApiLimit = async (limit: number) => {
    const response = await api.post("/admin/config/default-limit", { default_limit: limit });
    return response.data;
};

export const verifyUser = async (userId: string) => {
    const response = await api.post(`/admin/users/${userId}/verify`);
    return response.data;
};

export const resetUserApiKey = async (userId: string) => {
    const response = await api.post(`/admin/users/${userId}/reset-api-key`);
    return response.data;
};

export const adjustUserLimit = async (userId: string, limit: number) => {
    const response = await api.post(`/admin/users/${userId}/limit`, { limit });
    return response.data;
};

export const suspendUser = async (userId: string) => {
    const response = await api.post(`/admin/users/${userId}/suspend`);
    return response.data;
};

export const deleteUser = async (userId: string) => {
    const response = await api.delete(`/admin/users/${userId}`);
    return response.data;
};

export const deleteScan = async (scanId: string) => {
    const response = await api.delete(`/admin/scans/${scanId}`);
    return response.data;
};

export const updateAdminSettings = async (settings: any) => {
    const response = await api.post("/admin/config/settings", settings);
    return response.data;
};

export default api;
