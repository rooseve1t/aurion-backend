import React from 'react';

/**
 * 🌐 Aurion Marketing Website (Landing Page)
 * Design DNA for public-facing acquisition.
 */
export const LandingPage: React.FC = () => {
  return (
    <div className="bg-[#020617] text-white font-body selection:bg-cyan-500/30 overflow-x-hidden">
      
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center p-6">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 aurion-grid-bg opacity-10" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-500/10 blur-[150px] rounded-full animate-pulse" />
        
        <div className="relative z-10 text-center max-w-4xl mx-auto">
          <div className="inline-block px-4 py-1 glass rounded-full border border-cyan-500/30 text-[10px] font-mono text-cyan-400 uppercase tracking-[0.3em] mb-8 animate-bounce">
            Stage_23_Strategic_Intelligence
          </div>
          <h1 className="text-6xl md:text-8xl font-display font-black tracking-tighter mb-6 bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-slate-500">
            AURION <span className="text-cyan-400">OS</span>
          </h1>
          <p className="text-xl md:text-2xl text-slate-400 font-light tracking-wide mb-12 max-w-2xl mx-auto leading-relaxed">
            Beyond a personal assistant. A distributed <span className="text-white italic">Quantum-ready</span> neural network for the modern pioneer.
          </p>
          
          <div className="flex flex-col md:flex-row items-center justify-center gap-6">
            <button className="group relative px-12 py-4 bg-cyan-500 text-[#020617] font-display font-bold tracking-[0.2em] uppercase rounded-lg overflow-hidden transition-all hover:scale-105 active:scale-95">
              <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-500" />
              Initialize_Core
            </button>
            <button className="px-12 py-4 glass border border-white/10 text-white font-display font-bold tracking-[0.2em] uppercase rounded-lg hover:bg-white/5 transition-all">
              Read_Documentation
            </button>
          </div>
        </div>

        {/* Floating Core Hint */}
        <div className="absolute bottom-12 left-1/2 -translate-x-1/2 animate-bounce opacity-50">
          <div className="w-6 h-10 border-2 border-white/20 rounded-full flex justify-center p-2">
            <div className="w-1 h-2 bg-cyan-400 rounded-full animate-scroll" />
          </div>
        </div>
      </section>

      {/* Feature Grid: Strategic Pillars */}
      <section className="py-32 px-6 max-w-7xl mx-auto">
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { 
              title: 'Quantum_Bridge', 
              desc: 'Seamlessly distribute heavy reasoning tasks to global quantum clusters (IBM, D-Wave).',
              icon: '⚛️'
            },
            { 
              title: 'Sentinel_Active', 
              desc: 'Real-time darknet monitoring and automated network perimeter defense.',
              icon: '🛡️'
            },
            { 
              title: 'Project_Fabricator', 
              desc: 'Autonomous code synthesis. JARVIS builds your blueprints while you dream.',
              icon: '🏗️'
            }
          ].map((feature) => (
            <div key={feature.title} className="glass p-10 rounded-3xl border border-white/5 hover:border-cyan-500/30 transition-all group">
              <div className="text-4xl mb-6 group-hover:scale-110 transition-transform">{feature.icon}</div>
              <h3 className="text-xl font-display tracking-widest text-white mb-4 uppercase">{feature.title}</h3>
              <p className="text-slate-400 leading-relaxed font-light">{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Social Proof / Trust HUD */}
      <footer className="py-12 border-t border-white/5 text-center">
        <div className="text-[10px] font-mono text-slate-600 uppercase tracking-[0.5em] mb-4">
          AURION_INTELLIGENCE_NETWORK_GLOBAL
        </div>
        <p className="text-slate-500 text-sm">© 2026 Aurion OS. Developed for the future of humanity.</p>
      </footer>

    </div>
  );
};
