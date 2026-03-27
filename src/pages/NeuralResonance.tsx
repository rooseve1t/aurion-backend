import React, { useState, useEffect, useRef } from 'react';
import { Mic, CheckCircle, Activity, Zap } from 'lucide-react';

export const NeuralResonance: React.FC = () => {
  const [isCalibrating, setIsCalibrating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('IDLE');
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!isCalibrating) return;

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          setIsCalibrating(false);
          setStatus('SYNC_COMPLETE');
          return 100;
        }
        return prev + 2;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isCalibrating]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId: number;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.beginPath();
      ctx.strokeStyle = '#00f3ff';
      ctx.lineWidth = 2;

      for (let i = 0; i < canvas.width; i++) {
        const x = i;
        const amplitude = isCalibrating ? 30 : 5;
        const frequency = isCalibrating ? 0.05 : 0.02;
        const y = (canvas.height / 2) + Math.sin(i * frequency + Date.now() * 0.01) * amplitude;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();
      animationId = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(animationId);
  }, [isCalibrating]);

  const startCalibration = () => {
    setIsCalibrating(true);
    setProgress(0);
    setStatus('CALIBRATING...');
  };

  return (
    <div className="p-8 cyber-dashboard min-h-screen">
      <div className="max-w-2xl mx-auto space-y-8">
        <div className="flex items-center gap-4 mb-12">
          <Zap className="text-cyan-400 animate-pulse" size={32} />
          <h1 className="text-3xl font-display neon-text">Neural_Resonance_V1</h1>
        </div>

        <div className="quantum-glass p-8 space-y-6">
          <div className="flex justify-between items-center">
            <span className="text-xs font-mono text-slate-500 uppercase tracking-widest">Voice_Profile_Sync</span>
            <span className={`text-xs font-mono ${status === 'SYNC_COMPLETE' ? 'text-green-400' : 'text-cyan-400'}`}>{status}</span>
          </div>

          <canvas ref={canvasRef} width={600} height={150} className="w-full bg-black/40 rounded-lg border border-cyan-500/20" />

          <div className="space-y-2">
            <div className="flex justify-between text-[10px] font-mono text-slate-400 uppercase">
              <span>Calibration_Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-cyan-500 shadow-[0_0_10px_rgba(0,243,255,0.8)] transition-all duration-300" 
                style={{ width: `${progress}%` }} 
              />
            </div>
          </div>

          <div className="flex justify-center pt-4">
            {!isCalibrating && status !== 'SYNC_COMPLETE' ? (
              <button 
                onClick={startCalibration}
                className="flex items-center gap-3 px-8 py-3 bg-cyan-500/10 border border-cyan-500/50 text-cyan-400 rounded-xl hover:bg-cyan-500/20 transition-all group"
              >
                <Mic size={20} className="group-hover:scale-110 transition-transform" />
                <span className="font-mono uppercase tracking-widest text-sm">Start_Resonance</span>
              </button>
            ) : status === 'SYNC_COMPLETE' ? (
              <div className="flex items-center gap-3 text-green-400 font-mono uppercase tracking-widest">
                <CheckCircle size={24} />
                <span>VoiceID_Optimized</span>
              </div>
            ) : (
              <div className="flex items-center gap-3 text-cyan-400/60 font-mono animate-pulse uppercase tracking-widest">
                <Activity size={20} />
                <span>Analyzing_Acoustics...</span>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Tonal_Purity', val: '0.998' },
            { label: 'Neural_Match', val: '99.4%' },
            { label: 'Latency_Offset', val: '12ms' }
          ].map((stat, i) => (
            <div key={i} className="quantum-glass p-4 text-center">
              <p className="text-[8px] font-mono text-slate-500 uppercase mb-1">{stat.label}</p>
              <p className="text-sm font-display text-white">{stat.val}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
