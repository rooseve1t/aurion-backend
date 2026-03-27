import React, { useState } from 'react';
import { File, Lock, Unlock, Download, Trash2, Search } from 'lucide-react';

export const QuantumVault: React.FC = () => {
  const [files] = useState([
    { name: 'Blueprint_Mark_85.pdf', size: '12.4 MB', date: '2024-03-20', type: 'quantum-enc' },
    { name: 'Access_Codes_Omega.txt', size: '1.2 KB', date: '2024-03-21', type: 'quantum-enc' },
    { name: 'Financial_Forecast_Q4.xlsx', size: '4.5 MB', date: '2024-03-22', type: 'quantum-enc' },
  ]);

  const [isLocked, setIsCalibrating] = useState(true);

  return (
    <div className="p-8 cyber-dashboard min-h-screen">
      <div className="max-w-5xl mx-auto space-y-8">
        <div className="flex justify-between items-center mb-12">
          <div className="flex items-center gap-4">
            <Lock className="text-cyan-400" size={32} />
            <h1 className="text-3xl font-display neon-text">Quantum_Vault_V1</h1>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 quantum-glass">
            <div className={`w-2 h-2 rounded-full ${isLocked ? 'bg-red-500' : 'bg-green-500'} animate-pulse`} />
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">
              {isLocked ? 'Encrypted_State' : 'Vault_Accessible'}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Stats Sidebar */}
          <aside className="lg:col-span-1 space-y-6">
            <div className="quantum-glass p-6 space-y-4">
              <h3 className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Vault_Statistics</h3>
              <div className="space-y-3">
                {[
                  { label: 'Total_Files', val: '128' },
                  { label: 'Used_Space', val: '4.2 GB' },
                  { label: 'Encryption', val: 'Q-AES-256' },
                  { label: 'Fidelity', val: '0.9999' }
                ].map((s, i) => (
                  <div key={i} className="flex justify-between text-[11px] font-mono">
                    <span className="text-slate-500">{s.label}</span>
                    <span className="text-cyan-400">{s.val}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <button 
              onClick={() => setIsCalibrating(!isLocked)}
              className={`w-full py-4 rounded-xl font-mono uppercase tracking-widest text-xs flex items-center justify-center gap-3 transition-all ${
                isLocked ? 'bg-cyan-500/10 border border-cyan-500/50 text-cyan-400 hover:bg-cyan-500/20' : 'bg-green-500/10 border border-green-500/50 text-green-400'
              }`}
            >
              {isLocked ? <Unlock size={16} /> : <Lock size={16} />}
              {isLocked ? 'Authorize_Access' : 'Seal_Vault'}
            </button>
          </aside>

          {/* File Explorer */}
          <main className="lg:col-span-3 space-y-6">
            <div className="quantum-glass p-4 flex items-center gap-4">
              <Search size={18} className="text-slate-500" />
              <input 
                type="text" 
                placeholder="Search encrypted repository..." 
                className="bg-transparent border-none outline-none text-sm font-mono text-white w-full placeholder:text-slate-600"
              />
            </div>

            <div className="quantum-glass overflow-hidden">
              <table className="w-full text-left font-mono text-[11px]">
                <thead className="bg-black/40 text-slate-500 uppercase tracking-widest">
                  <tr>
                    <th className="px-6 py-4 font-normal">File_Name</th>
                    <th className="px-6 py-4 font-normal">Size</th>
                    <th className="px-6 py-4 font-normal">Date_Stored</th>
                    <th className="px-6 py-4 font-normal text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {files.map((file, i) => (
                    <tr key={i} className="hover:bg-cyan-500/5 transition-colors group">
                      <td className="px-6 py-4 flex items-center gap-3">
                        <File size={14} className="text-cyan-400/60" />
                        <span className="text-slate-200">{file.name}</span>
                      </td>
                      <td className="px-6 py-4 text-slate-400">{file.size}</td>
                      <td className="px-6 py-4 text-slate-500">{file.date}</td>
                      <td className="px-6 py-4 text-right space-x-4">
                        <button className="text-slate-500 hover:text-cyan-400 transition-colors"><Download size={14} /></button>
                        <button className="text-slate-500 hover:text-red-400 transition-colors"><Trash2 size={14} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {isLocked && (
                <div className="absolute inset-0 bg-black/60 backdrop-blur-md flex flex-col items-center justify-center space-y-4">
                  <Lock size={48} className="text-cyan-500/40 animate-pulse" />
                  <p className="font-mono text-xs text-slate-400 uppercase tracking-[0.3em]">Access_Restricted</p>
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};
