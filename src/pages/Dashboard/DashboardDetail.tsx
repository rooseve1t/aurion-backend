import React from 'react';
import { AurionTheme, UI_COMPONENTS } from '@/styles/design_system';
import { Core3DScene } from '@/components/Core3D/Core3DScene';
import { SentinelWidget } from '@/components/Widgets/SentinelWidget';
import { FortuneWidget } from '@/components/Widgets/FortuneWidget';
import { FabricatorWidget } from '@/components/Widgets/FabricatorWidget';

/**
 * 🖥️ Aurion Web Application - Strategic Dashboard
 * The primary interface for Stage 23+
 */
export const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#020617] text-slate-50 font-body overflow-hidden selection:bg-cyan-500/30">
      {/* Background Grid & Ambient Glow */}
      <div className="absolute inset-0 aurion-grid-bg opacity-20 pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-cyan-500/5 blur-[120px] rounded-full pointer-events-none" />

      {/* Main Layout */}
      <div className="relative z-10 flex flex-col h-screen p-6 gap-6">
        
        {/* Top Navigation / HUD Bar */}
        <header className="flex justify-between items-center h-16 px-8 glass rounded-2xl border-l-4 border-cyan-500 animate-slide-in">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <span className="font-display text-xl font-black">A</span>
            </div>
            <div>
              <h1 className="font-display text-lg tracking-widest text-white leading-none">AURION_OS</h1>
              <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-tighter opacity-70">Strategic Intelligence System v23.4.2</span>
            </div>
          </div>
          
          <nav className="flex items-center gap-8">
            {['Dashboard', 'Fabricator', 'Quantum', 'Guardian', 'Vault'].map((item) => (
              <a key={item} href={`#${item.toLowerCase()}`} className="text-sm font-display tracking-widest text-slate-400 hover:text-cyan-400 transition-colors duration-300 uppercase">
                {item}
              </a>
            ))}
          </nav>

          <div className="flex items-center gap-6">
            <div className="text-right">
              <div className="text-xs font-mono text-purple-400">COGNITIVE_SYNC</div>
              <div className="text-sm font-bold text-white tracking-widest">99.9%_STABLE</div>
            </div>
            <div className="w-12 h-12 rounded-full border-2 border-slate-700 p-1">
              <img src="/avatar_founder.jpg" alt="Founder" className="w-full h-full rounded-full object-cover" />
            </div>
          </div>
        </header>

        {/* Content Grid */}
        <main className="flex-1 grid grid-cols-12 gap-6 overflow-hidden">
          
          {/* Left Sidebar: Assets & Intelligence */}
          <aside className="col-span-3 flex flex-col gap-6 animate-slide-in">
            <FortuneWidget />
            <div className="flex-1 glass rounded-2xl p-6 overflow-y-auto">
              <h3 className="font-display text-xs text-slate-400 tracking-widest uppercase mb-4">Neural_Memory_Logs</h3>
              <div className="space-y-4 font-mono text-xs">
                {[1,2,3,4,5].map(i => (
                  <div key={i} className="p-3 rounded bg-slate-900/50 border-l-2 border-purple-500/50">
                    <span className="text-purple-400">[INSIGHT_{i}]</span> New correlation detected between market volatility and local code-base stability.
                  </div>
                ))}
              </div>
            </div>
          </aside>

          {/* Center: 3D Holographic Workshop */}
          <section className="col-span-6 relative glass rounded-3xl overflow-hidden group">
            <div className="absolute inset-0 z-0">
              <Core3DScene />
            </div>
            
            {/* HUD Overlays */}
            <div className="absolute top-6 left-6 pointer-events-none">
              <div className="text-[10px] font-mono text-cyan-500/50">CORE_REALTIME_VISUALIZATION</div>
            </div>
            
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-12 pointer-events-none">
              <div className="text-center">
                <div className="text-[10px] font-mono text-slate-500 mb-1">PULSE</div>
                <div className="text-xl font-display text-white animate-pulse">72_BPM</div>
              </div>
              <div className="text-center">
                <div className="text-[10px] font-mono text-slate-500 mb-1">RESONANCE</div>
                <div className="text-xl font-display text-cyan-400">CALM</div>
              </div>
              <div className="text-center">
                <div className="text-[10px] font-mono text-slate-500 mb-1">THREATS</div>
                <div className="text-xl font-display text-red-500">00</div>
              </div>
            </div>
          </section>

          {/* Right Sidebar: Operations & Security */}
          <aside className="col-span-3 flex flex-col gap-6 animate-slide-in-right">
            <SentinelWidget />
            <FabricatorWidget />
            <div className="glass rounded-2xl p-6 border-b-4 border-yellow-500">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-display text-xs text-yellow-500 tracking-widest uppercase">System_Fabricator</h3>
                <span className="text-[10px] font-mono bg-yellow-500/20 text-yellow-500 px-2 py-0.5 rounded">READY</span>
              </div>
              <p className="text-sm text-slate-400 mb-4">Awaiting blueprint synthesis instructions...</p>
              <button className="w-full py-2 bg-yellow-500/10 border border-yellow-500/30 text-yellow-500 font-display text-xs tracking-widest hover:bg-yellow-500/20 transition-all uppercase">
                Initialize_Project
              </button>
            </div>
          </aside>

        </main>

        {/* Bottom HUD: Global Status & Mission Progress */}
        <footer className="h-12 flex items-center justify-between px-8 glass rounded-xl text-[10px] font-mono text-slate-500">
          <div className="flex gap-8">
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" /> QUANTUM_LINK: ACTIVE</span>
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" /> VPN_STATUS: ENCRYPTED</span>
            <span className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-purple-500" /> VAULT_SECURITY: MAX</span>
          </div>
          <div className="text-cyan-500 animate-pulse tracking-[0.2em]">
            SYSTEM_UPTIME: 42:13:37:00
          </div>
        </footer>

      </div>
    </div>
  );
};
