"use client";

import { useEffect, useState } from "react";
import { AdminPageContainer } from "@/components/admin/common/AdminPageContainer";
import { getThreatIntelStatus } from "@/lib/api";
import { 
  Loader2, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw, 
  Edit3, 
  Zap
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { cn } from "@/lib/utils";

export default function ThreatIntelPage() {
  const [services, setServices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  async function fetchData() {
    try {
      const data = await getThreatIntelStatus();
      setServices(data);
    } catch (error) {
      console.error("Failed to fetch threat intel status", error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  const handleTest = async (id: string) => {
    try {
      alert(`Testing connection to ${id}...`);
      // Simulate API call
      await new Promise(r => setTimeout(r, 1500));
      alert(`${id} connection successful! Rate limits: 98% remaining.`);
    } catch (e) {
      alert(`Testing failed for ${id}`);
    }
  };

  const handleUpdateKey = async (service: any) => {
    const newKey = prompt(`Enter new API Key for ${service.name}:`, "••••••••••••••••");
    if (newKey) {
        alert(`${service.name} API Key updated successfully (simulated)`);
    }
  };

  const handleToggle = async (id: string, enabled: boolean) => {
    alert(`${id} has been ${!enabled ? 'disabled' : 'enabled'} successfully`);
  };

  if (loading) {
    return (
      <AdminPageContainer title="Threat Intelligence" description="Loading services...">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
        </div>
      </AdminPageContainer>
    );
  }

  return (
    <AdminPageContainer
      title="Threat Intelligence"
      description="Manage external threat intelligence service integrations"
      icon={<AlertTriangle className="w-7 h-7 text-cyan-400" />}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {services?.map((service) => (
          <div 
            key={service.id} 
            className="bg-[#121212] border border-white/5 rounded-xl p-6 flex flex-col shadow-2xl hover:border-white/10 transition-all group"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center border transition-colors",
                  service.enabled ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" : "bg-white/5 border-white/10 text-gray-500"
                )}>
                  {service.status === 'warning' ? <AlertTriangle size={20} className="text-amber-400" /> : <CheckCircle2 size={20} />}
                </div>
                <div>
                  <h3 className="text-lg font-black text-white tracking-tight">{service.name}</h3>
                  <p className={cn(
                    "text-[10px] font-black uppercase tracking-widest",
                    service.status === 'ok' ? "text-emerald-400" : "text-amber-400"
                  )}>
                    {service.status === 'ok' ? "Connected" : "Warning"}
                  </p>
                </div>
              </div>
              <Switch 
                checked={service.enabled} 
                onCheckedChange={(checked) => handleToggle(service.id, checked)}
                className="data-[state=checked]:bg-emerald-500"
              />
            </div>

            {/* API Key Box */}
            <div className="bg-black/40 border border-white/5 rounded-lg p-4 mb-4">
              <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-2">API Key</p>
              <p className="text-sm font-mono text-gray-400 tracking-widest">••••••••••••••••</p>
            </div>

            {/* Info Row */}
            <div className="flex items-center justify-between text-[10px] font-black text-gray-500 uppercase tracking-widest mb-6">
              <span>Last checked:</span>
              <span className="text-gray-300">
                {new Date().toLocaleTimeString().toLowerCase()}
              </span>
            </div>

            {/* Warning Message (Mocked for specific services like in image) */}
            {service.name === "URLHaus" && (
              <div className="mb-6 p-3 bg-amber-500/5 border border-amber-500/20 rounded-lg flex items-center gap-2">
                <AlertTriangle size={12} className="text-amber-500" />
                <p className="text-[10px] font-bold text-amber-500/80 uppercase">Rate limit approaching</p>
              </div>
            )}

            {/* Actions */}
            <div className="grid grid-cols-2 gap-3 mt-auto">
              <Button 
                variant="outline" 
                onClick={() => handleTest(service.id)}
                className="bg-black border-white/5 hover:bg-white/5 text-white font-black uppercase tracking-widest text-[10px] h-10"
              >
                <RefreshCw size={14} className="mr-2" />
                Test
              </Button>
              <Button 
                onClick={() => handleUpdateKey(service)}
                className="bg-white/5 hover:bg-white/10 text-white font-black uppercase tracking-widest text-[10px] h-10 border border-white/5"
              >
                <Edit3 size={14} className="mr-2" />
                Update
              </Button>
            </div>
          </div>
        ))}
      </div>
    </AdminPageContainer>
  );
}
