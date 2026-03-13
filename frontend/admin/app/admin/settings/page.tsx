/**
 * Admin Settings
 * System configuration and preferences
 */

"use client";

import { Settings, Save, RotateCcw, Toggle, Loader2 } from "lucide-react";
import { AdminPageContainer } from "@/components/admin/common/AdminPageContainer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState } from "react";
import { updateAdminSettings } from "@/lib/api";

export default function SettingsPage() {
  const [isSaving, setIsSaving] = useState(false);
  const [platformName, setPlatformName] = useState("ReconXplorer");
  const [supportEmail, setSupportEmail] = useState("support@reconxplorer.dev");
  const [maxScanDuration, setMaxScanDuration] = useState(120);
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [maintenanceMode, setMaintenanceMode] = useState(false);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await updateAdminSettings({
        platform_name: platformName,
        support_email: supportEmail,
        max_scan_duration: maxScanDuration,
        email_alerts: emailAlerts,
        maintenance_mode: maintenanceMode
      });
      alert("Settings saved successfully");
    } catch (error) {
      alert("Failed to save settings");
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (confirm("Reset all settings to defaults?")) {
        setPlatformName("ReconXplorer");
        setSupportEmail("support@reconxplorer.dev");
        setMaxScanDuration(120);
        setEmailAlerts(true);
        setMaintenanceMode(false);
    }
  };

  return (
    <AdminPageContainer
      title="System Settings"
      description="Configure platform behavior and preferences"
      icon={<Settings className="w-7 h-7" />}
    >
      {/* General Settings */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-white">General</h2>

        <div className="bg-gray-900/50 glass-effect rounded-lg p-6 border border-gray-800 space-y-6">
          {/* Platform Name */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Platform Name
            </label>
            <Input
              value={platformName}
              onChange={(e) => setPlatformName(e.target.value)}
              className="bg-gray-800 border-gray-700 text-white"
            />
            <p className="text-xs text-gray-500 mt-1">
              Displayed in notifications and emails
            </p>
          </div>

          {/* Support Email */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Support Email
            </label>
            <Input
              value={supportEmail}
              onChange={(e) => setSupportEmail(e.target.value)}
              className="bg-gray-800 border-gray-700 text-white"
            />
          </div>

          {/* Max Scan Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Max Scan Duration (minutes)
            </label>
            <Input
              type="number"
              value={maxScanDuration}
              onChange={(e) => setMaxScanDuration(parseInt(e.target.value))}
              className="bg-gray-800 border-gray-700 text-white"
            />
            <p className="text-xs text-gray-500 mt-1">
              Scans exceeding this will auto-timeout
            </p>
          </div>
        </div>
      </div>

      {/* Alert Settings */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-white">Alerts & Notifications</h2>

        <div className="bg-gray-900/50 glass-effect rounded-lg p-6 border border-gray-800 space-y-4">
          {/* Email Alerts */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-300">Email Alerts on Critical Findings</p>
              <p className="text-xs text-gray-500 mt-1">
                Send email notification when critical vulnerabilities are found
              </p>
            </div>
            <input 
                type="checkbox" 
                checked={emailAlerts} 
                onChange={(e) => setEmailAlerts(e.target.checked)}
                className="w-5 h-5 accent-cyan-500" 
            />
          </div>
        </div>
      </div>

      {/* Maintenance Mode */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-white">Maintenance</h2>

        <div className="bg-gray-900/50 glass-effect rounded-lg p-6 border border-gray-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-300">Maintenance Mode</p>
              <p className="text-xs text-gray-500 mt-1">
                Disable all scans and restrict user access
              </p>
            </div>
            <input 
                type="checkbox" 
                checked={maintenanceMode} 
                onChange={(e) => setMaintenanceMode(e.target.checked)}
                className="w-5 h-5 accent-red-500" 
            />
          </div>

          {maintenanceMode && (
            <div className="mt-4 p-3 bg-amber-500/10 border border-amber-500/30 rounded">
                <p className="text-xs text-amber-300">
                Maintenance mode is currently ACTIVE. Users cannot initiate new scans.
                </p>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 justify-end pt-6 border-t border-gray-800">
        <Button
          variant="outline"
          onClick={handleReset}
          className="flex items-center gap-2"
        >
          <RotateCcw className="w-4 h-4" />
          Reset to Defaults
        </Button>
        <Button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 text-white"
        >
          {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          {isSaving ? "Saving..." : "Save Changes"}
        </Button>
      </div>
    </AdminPageContainer>
  );
}

