/**
 * 🧬 Aurion Design System (The DNA)
 * Unified configuration for Web, Mobile, and Desktop.
 */

export const AurionTheme = {
  colors: {
    primary: {
      core: '#00f2ff', // Bioluminescent Cyan
      glow: 'rgba(0, 242, 255, 0.5)',
      dark: '#083344',
    },
    secondary: {
      core: '#8b5cf6', // Strategic Purple
      glow: 'rgba(139, 92, 246, 0.5)',
    },
    accent: {
      danger: '#ef4444', // Sentinel Red
      warning: '#f59e0b', // Fabricator Gold
      success: '#10b981', // Quantum Green
    },
    background: {
      deep: '#020617', // Space Black
      glass: 'rgba(15, 23, 42, 0.7)',
      border: 'rgba(255, 255, 255, 0.1)',
    },
    text: {
      main: '#f8fafc',
      muted: '#94a3b8',
      dim: '#64748b',
    }
  },
  typography: {
    fontFamily: {
      display: '"Orbitron", sans-serif', // Tech/HUD style
      body: '"Inter", sans-serif',      // Clean UI
      mono: '"Fira Code", monospace',   // Data/Logs
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '4xl': '2.25rem',
    }
  },
  effects: {
    glass: 'backdrop-blur-xl bg-slate-900/70 border border-white/10',
    glow: 'shadow-[0_0_20px_rgba(0,242,255,0.3)]',
    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  }
};

export const UI_COMPONENTS = {
  Card: `glass rounded-2xl p-6 hover:border-cyan-500/50 transition-all duration-500`,
  Button: `px-6 py-2 rounded-lg font-bold tracking-widest uppercase transition-all duration-300`,
  Input: `bg-slate-950/50 border border-white/10 rounded-lg px-4 py-2 text-white focus:border-cyan-500 outline-none`,
  HUD_Text: `font-display tracking-tighter uppercase text-cyan-400`,
};
