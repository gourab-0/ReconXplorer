"use client";

import { X, Check, ShieldAlert, Activity, Globe, Download, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ScanDetailsModalProps {
  scan: any;
  onClose: () => void;
}

export function ScanDetailsModal({ scan, onClose }: ScanDetailsModalProps) {
  if (!scan) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />
      
      <div className="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col relative z-10 shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-gray-800 flex items-start justify-between bg-gray-900/50">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h2 className="text-xl font-bold text-white uppercase tracking-tight">Operation Artifact</h2>
              <span className={cn(
                "px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-widest border",
                scan.status === 'completed' ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : "bg-amber-500/10 text-amber-400 border-amber-500/20"
              )}>
                {scan.status}
              </span>
            </div>
            <p className="text-xs text-gray-500 font-mono">
              TARGET: <span className="text-cyan-400">{scan.target_value || scan.target}</span>
              <span className="mx-2">|</span>
              ID: <span className="text-gray-400">{scan.id}</span>
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-lg text-gray-500 hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8 bg-black/20">
          {/* Risk Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-gray-800/40 border border-gray-700/50 rounded-xl">
              <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Risk Level</p>
              <p className={cn(
                "text-2xl font-black uppercase italic",
                scan.risk_level === 'high' || scan.risk_level === 'critical' ? "text-red-400" : "text-emerald-400"
              )}>
                {scan.risk_level || 'N/A'}
              </p>
            </div>
            <div className="p-4 bg-gray-800/40 border border-gray-700/50 rounded-xl">
              <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Risk Score</p>
              <p className="text-2xl font-black text-white italic">{scan.risk_score || 0}</p>
            </div>
            <div className="p-4 bg-gray-800/40 border border-gray-700/50 rounded-xl">
              <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Findings</p>
              <p className="text-2xl font-black text-cyan-400 italic">{scan.findings_count || 0}</p>
            </div>
          </div>

          {/* AI Insights (If any) */}
          <div className="space-y-3">
             <h3 className="flex items-center gap-2 text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">
               <Activity size={14} className="text-cyan-400" /> AI intelligence report
             </h3>
             <div className="p-5 bg-cyan-500/5 border border-cyan-500/20 rounded-2xl">
               <p className="text-sm text-gray-300 leading-relaxed italic">
                 {scan.ai_summary || "Automated intelligence analysis has not been synthesized for this artifact."}
               </p>
             </div>
          </div>

          {/* Technical Data Tabs simulation */}
          <div className="space-y-3">
             <h3 className="flex items-center gap-2 text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1">
               <Clock size={14} className="text-gray-500" /> Operational timestamps
             </h3>
             <div className="bg-gray-800/30 border border-gray-800 rounded-xl overflow-hidden divide-y divide-gray-800">
               <div className="flex justify-between p-3 px-4">
                 <span className="text-[10px] font-bold text-gray-500 uppercase">Deployed At</span>
                 <span className="text-xs text-gray-300 font-mono">{new Date(scan.created_at).toLocaleString()}</span>
               </div>
               <div className="flex justify-between p-3 px-4">
                 <span className="text-[10px] font-bold text-gray-500 uppercase">Synchronized At</span>
                 <span className="text-xs text-gray-300 font-mono">{scan.finished_at ? new Date(scan.finished_at).toLocaleString() : 'PENDING'}</span>
               </div>
             </div>
          </div>

          {/* Raw Output Placeholder */}
          <div className="space-y-3">
             <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-widest ml-1">Technical logs</h3>
             <div className="bg-black p-4 border border-gray-800 rounded-xl h-48 overflow-y-auto custom-scrollbar">
               <pre className="text-[10px] text-emerald-500/80 font-mono">
                 {scan.error ? `[ERROR] ${scan.error}` : scan.output || '[SYSTEM] No raw output logs available for this artifact.'}
               </pre>
             </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 px-6 border-t border-gray-800 flex justify-end gap-3 bg-gray-900/50">
          <Button variant="outline" className="text-[10px] font-black uppercase tracking-widest border-gray-800 h-10 px-6">
            <Download size={14} className="mr-2" /> Export Artifact
          </Button>
          <Button onClick={onClose} className="text-[10px] font-black uppercase tracking-widest bg-cyan-600 hover:bg-cyan-500 text-white h-10 px-8 min-w-[120px]">
            Acknowledge
          </Button>
        </div>
      </div>
    </div>
  );
}
