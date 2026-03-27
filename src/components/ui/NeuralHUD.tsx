import React, { useMemo } from 'react';

export const NeuralHUD: React.FC<{ active?: boolean }> = ({ active }) => {
  const points = useMemo(() => {
    return Array.from({ length: 20 }).map((_, i) => ({
      id: i,
      x: 50 + 40 * Math.cos((i * 2 * Math.PI) / 20),
      y: 50 + 40 * Math.sin((i * 2 * Math.PI) / 20),
    }));
  }, []);

  return (
    <div className={`relative w-64 h-64 transition-all duration-1000 ${active ? 'opacity-100 scale-100' : 'opacity-30 scale-95'}`}>
      <svg viewBox="0 0 100 100" className="w-full h-full">
        {/* Connection lines */}
        {points.map((p, i) => (
          points.slice(i + 1).map((p2, j) => (
            <line
              key={`${i}-${j}`}
              x1={p.x}
              y1={p.y}
              x2={p2.x}
              y2={p2.y}
              stroke="var(--quantum-cyan)"
              strokeWidth="0.1"
              strokeDasharray="2 2"
              className="animate-pulse"
              style={{ animationDelay: `${(i + j) * 0.1}s` }}
            />
          ))
        ))}
        
        {/* Neurons */}
        {points.map((p) => (
          <circle
            key={p.id}
            cx={p.x}
            cy={p.y}
            r="1.5"
            fill="var(--quantum-cyan)"
            className={`${active ? 'animate-ping' : ''}`}
            style={{ animationDuration: '3s' }}
          />
        ))}
        
        {/* Center Core */}
        <circle
          cx="50"
          cy="50"
          r="5"
          fill="none"
          stroke="var(--quantum-cyan)"
          strokeWidth="0.5"
          className="animate-spin-slow"
          style={{ strokeDasharray: '5 5' }}
        />
        <circle
          cx="50"
          cy="50"
          r="2"
          fill="var(--quantum-magenta)"
          className="animate-pulse"
        />
      </svg>
      
      {/* Decorative HUD Elements */}
      <div className="absolute inset-0 border border-cyan-500/20 rounded-full animate-spin-slow" />
      <div className="absolute inset-2 border border-purple-500/10 rounded-full animate-reverse-spin" />
    </div>
  );
};
