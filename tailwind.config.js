/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:      '#000000',
        card:    '#0a1214',
        cyan:    '#00e5ff',
        amber:   '#f59e0b',
        purple:  '#a855f7',
        emerald: '#10b981',
        danger:  '#ef4444',
        teal:    '#06b6d4',
        surface: '#0d1f24',
      },
      fontFamily: { mono: ['JetBrains Mono', 'Fira Code', 'monospace'] },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'glow':       'glow 2s ease-in-out infinite alternate',
        'slide-in':   'slideIn 0.3s ease-out',
        'fade-in':    'fadeIn 0.4s ease-out',
      },
      keyframes: {
        glow:    { '0%': { opacity: '0.7' }, '100%': { opacity: '1', filter: 'drop-shadow(0 0 8px #00e5ff)' }},
        slideIn: { from: { transform: 'translateX(-100%)', opacity: '0' }, to: { transform: 'translateX(0)', opacity: '1' }},
        fadeIn:  { from: { opacity: '0', transform: 'translateY(8px)' }, to: { opacity: '1', transform: 'translateY(0)' }},
      },
    },
  },
  plugins: [],
}
