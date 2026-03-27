import React from 'react';
import { UI_COMPONENTS } from '@/styles/design_system';
import { Hammer, Code, Rocket, Terminal } from 'lucide-react';

export const FabricatorWidget: React.FC = () => {
  return (
    <div className={UI_COMPONENTS.Card}>
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="font-display text-xs text-slate-400 tracking-widest uppercase">Project_Fabricator</h3>
          <div className="text-2xl font-display text-white mt-1 tracking-tighter">IDLE</div>
        </div>
        <div className="p-2 rounded-lg bg-yellow-500/10 text-yellow-400">
          <Hammer size={20} />
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border-l-2 border-yellow-500">
          <div className="flex items-center gap-3">
            <Code size={14} className="text-yellow-400" />
            <span className="text-xs font-mono">Boilerplate_Gen</span>
          </div>
          <span className="text-xs font-mono text-yellow-400">READY</span>
        </div>

        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border-l-2 border-purple-500">
          <div className="flex items-center gap-3">
            <Terminal size={14} className="text-purple-400" />
            <span className="text-xs font-mono">Iron_Protocol</span>
          </div>
          <span className="text-xs font-mono text-purple-400">LOCKED</span>
        </div>

        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border-l-2 border-cyan-500">
          <div className="flex items-center gap-3">
            <Rocket size={14} className="text-cyan-400" />
            <span className="text-xs font-mono">Autonomous_Build</span>
          </div>
          <span className="text-xs font-mono text-cyan-400">PENDING</span>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-white/5">
        <div className="flex justify-between text-[10px] font-mono text-slate-500 uppercase mb-2">
          <span>Resource_Allocation</span>
          <span>Optimal</span>
        </div>
        <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
          <div className="w-[45%] h-full bg-yellow-500 shadow-[0_0_10px_#f59e0b]" />
        </div>
      </div>
    </div>
  );
};
