import React from 'react';
import { UI_COMPONENTS } from '@/styles/design_system';
import { TrendingUp, Wallet, DollarSign, Activity } from 'lucide-react';

export const FortuneWidget: React.FC = () => {
  return (
    <div className={UI_COMPONENTS.Card}>
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="font-display text-xs text-slate-400 tracking-widest uppercase">Financial_Oracle</h3>
          <div className="text-2xl font-display text-white mt-1 tracking-tighter">$1.2M_AUM</div>
        </div>
        <div className="p-2 rounded-lg bg-green-500/10 text-green-400">
          <TrendingUp size={20} />
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border-l-2 border-green-500">
          <div className="flex items-center gap-3">
            <Wallet size={14} className="text-green-400" />
            <span className="text-xs font-mono">Portfolio_Growth</span>
          </div>
          <span className="text-xs font-mono text-green-400">+12.4%</span>
        </div>

        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border-l-2 border-purple-500">
          <div className="flex items-center gap-3">
            <DollarSign size={14} className="text-purple-400" />
            <span className="text-xs font-mono">Yield_Optimization</span>
          </div>
          <span className="text-xs font-mono text-purple-400">OPTIMAL</span>
        </div>

        <div className="flex items-center justify-between p-3 rounded bg-slate-900/50 border-l-2 border-cyan-500">
          <div className="flex items-center gap-3">
            <Activity size={14} className="text-cyan-400" />
            <span className="text-xs font-mono">Market_Sentiment</span>
          </div>
          <span className="text-xs font-mono text-cyan-400">BULLISH</span>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-white/5">
        <div className="flex justify-between text-[10px] font-mono text-slate-500 uppercase mb-2">
          <span>Oracle_Confidence</span>
          <span>98.2%</span>
        </div>
        <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
          <div className="w-[98%] h-full bg-green-500 shadow-[0_0_10px_#10b981]" />
        </div>
      </div>
    </div>
  );
};
