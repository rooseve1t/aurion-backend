import React, { useMemo } from 'react';
import { Shield, Zap } from 'lucide-react';

export const QuantumMap: React.FC<{ nodes: any[] }> = ({ nodes }) => {
  const defaultNodes = useMemo(() => [
    { id: 'Node-01', x: 20, y: 30, status: 'active' },
    { id: 'Node-02', x: 80, y: 20, status: 'active' },
    { id: 'Node-03', x: 50, y: 80, status: 'warning' },
    { id: 'Node-04', x: 10, y: 70, status: 'active' },
  ], []);

  const displayNodes = nodes.length > 0 ? nodes : defaultNodes;

  return (
    <div className="w-full h-48 quantum-glass relative overflow-hidden">
      <div className="absolute top-2 left-2 flex items-center gap-2">
        <Zap size={10} className="text-cyan-400" />
        <span className="text-[8px] font-mono text-slate-500 uppercase">Quantum_Mesh_Map</span>
      </div>
      
      <svg viewBox="0 0 100 100" className="w-full h-full p-4">
        {/* Connection lines */}
        {displayNodes.map((n, i) => (
          displayNodes.slice(i + 1).map((n2, j) => (
            <line
              key={`${i}-${j}`}
              x1={n.x}
              y1={n.y}
              x2={n2.x}
              y2={n2.y}
              stroke="var(--quantum-cyan)"
              strokeWidth="0.2"
              strokeOpacity="0.2"
              strokeDasharray="1 1"
            />
          ))
        ))}
        
        {/* Nodes */}
        {displayNodes.map((n) => (
          <g key={n.id}>
            <circle
              cx={n.x}
              cy={n.y}
              r="2"
              fill={n.status === 'active' ? 'var(--quantum-cyan)' : 'var(--quantum-magenta)'}
              className="animate-pulse"
            />
            <text
              x={n.x}
              y={n.y + 5}
              textAnchor="middle"
              fill="white"
              fontSize="3"
              fontFamily="monospace"
              className="opacity-50"
            >
              {n.id}
            </text>
          </g>
        ))}
      </svg>
      
      <div className="absolute bottom-2 right-2">
        <Shield size={12} className="text-cyan-500/20" />
      </div>
    </div>
  );
};
