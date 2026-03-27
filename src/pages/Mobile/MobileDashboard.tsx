import React from 'react';

/**
 * 📱 Aurion Mobile Design Philosophy
 * Optimized for one-hand strategic management.
 */
export const MobileDashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#020617] text-white font-body p-4 flex flex-col gap-4">
      {/* Dynamic Status Bar */}
      <div className="flex justify-between items-center h-8 px-2 text-[10px] font-mono text-cyan-500/50 uppercase tracking-widest">
        <span>JARVIS_OS_MOBILE</span>
        <div className="flex gap-2">
          <span>LTE_ENCRYPTED</span>
          <span className="animate-pulse">●</span>
        </div>
      </div>

      {/* Main Core View (Simplified for Mobile) */}
      <div className="h-64 glass rounded-3xl relative overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/10 to-transparent" />
        {/* Central Core Indicator */}
        <div className="w-32 h-32 rounded-full border border-cyan-500/30 flex items-center justify-center relative">
          <div className="absolute inset-0 rounded-full border border-cyan-500/10 animate-spin-slow" />
          <div className="w-16 h-16 rounded-full bg-cyan-500/20 blur-xl animate-pulse" />
          <span className="font-display text-2xl font-bold tracking-tighter text-white">A</span>
        </div>
        <div className="absolute bottom-4 text-center">
          <div className="text-xs font-mono text-cyan-400">RESONANCE: STABLE</div>
        </div>
      </div>

      {/* Grid of Modules */}
      <div className="grid grid-cols-2 gap-4">
        {[
          { label: 'SENTINEL', status: 'ACTIVE', color: 'red' },
          { label: 'FORTUNE', status: 'BULLISH', color: 'green' },
          { label: 'FABRICATOR', status: 'IDLE', color: 'yellow' },
          { label: 'VAULT', status: 'SECURE', color: 'purple' }
        ].map((mod) => (
          <div key={mod.label} className="glass p-4 rounded-2xl border-b-2 border-slate-800 active:scale-95 transition-all">
            <div className={`text-[10px] text-${mod.color}-500 font-mono mb-1`}>{mod.label}</div>
            <div className="text-sm font-display tracking-widest">{mod.status}</div>
          </div>
        ))}
      </div>

      {/* Intelligence Feed */}
      <div className="flex-1 glass rounded-2xl p-4 overflow-hidden">
        <h3 className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-3">Intelligence_Feed</h3>
        <div className="space-y-3">
          {[1,2,3].map(i => (
            <div key={i} className="flex gap-3 items-start opacity-80">
              <div className="w-1 h-8 bg-purple-500 rounded-full shrink-0" />
              <p className="text-[11px] font-mono text-slate-300">
                <span className="text-purple-400">#LOG_{i}:</span> Potential data anomaly detected in secondary network segment. Isolated.
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Voice Control Trigger */}
      <button className="h-16 w-full glass rounded-2xl border border-cyan-500/30 flex items-center justify-center gap-3 active:bg-cyan-500/10 transition-all">
        <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
        <span className="font-display text-sm tracking-[0.2em] text-cyan-400 uppercase">AWAITING_COMMAND</span>
      </button>
    </div>
  );
};
