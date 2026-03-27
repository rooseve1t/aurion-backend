import React from 'react';
import { AurionTheme, UI_COMPONENTS } from '@/styles/design_system';
import { Shield, Zap, AlertTriangle, Lock } from 'lucide-react';

export const SentinelWidget: React.FC = () => {
  return (
    <div className={UI_COMPONENTS.Card}>
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="font-display text-xs text-slate-400 tracking-widest uppercase">Sentinel_Protection</h3>
          <div className="text-2xl font-display text-white mt-1 tracking-tighter">ACTIVE</div>
        </div>
        <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 animate-pulse">
          <Shield size={20} />
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border-l-2 border-cyan-500">
          <div className="flex items-center gap-3">
            <Zap size={14} className="text-cyan-400" />
            <span className="text-xs font-mono">Firewall_Status</span>
          </div>
          <span className="text-xs font-mono text-cyan-400">ENFORCED</span>
        </div>

        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border-l-2 border-purple-500">
          <div className="flex items-center gap-3">
            <Lock size={14} className="text-purple-400" />
            <span className="text-xs font-mono">Encryption_Layer</span>
          </div>
          <span className="text-xs font-mono text-purple-400">AES-256-GCM</span>
        </div>

        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border-l-2 border-red-500">
          <div className="flex items-center gap-3">
            <AlertTriangle size={14} className="text-red-400" />
            <span className="text-xs font-mono">Intrusions_Blocked</span>
          </div>
          <span className="text-xs font-mono text-red-400">1,242</span>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-white/5">
        <div className="flex justify-between text-[10px] font-mono text-slate-500 uppercase mb-2">
          <span>Threat_Level</span>
          <span>Minimal</span>
        </div>
        <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
          <div className="w-[15%] h-full bg-cyan-500 shadow-[0_0_10px_#06b6d4]" />
        </div>
      </div>
    </div>
  );
};
