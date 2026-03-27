import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Activity, 
  Cpu, 
  Zap, 
  Shield, 
  Brain, 
  Terminal,
  Circle
} from 'lucide-react';
import styles from './SquadDashboard.module.css';

interface Employee {
  name: string;
  role: string;
  status: 'working' | 'standby' | 'error';
  last_action: string | null;
  performance: number;
}

const SquadDashboard: React.FC = () => {
  const [employees] = useState<Employee[]>([
    { name: 'Alpha', role: 'Architect', status: 'working', last_action: 'Sharding Memory Nodes', performance: 0.98 },
    { name: 'Sigma', role: 'Fullstack', status: 'standby', last_action: 'UI Bridge Synced', performance: 0.95 },
    { name: 'Lux', role: 'Designer', status: 'working', last_action: 'Rendering Shaders', performance: 0.99 },
    { name: 'Sentinel', role: 'SecOps', status: 'working', last_action: 'OSINT Scan Active', performance: 1.0 },
    { name: 'Synapse', role: 'Neuro-Scientist', status: 'working', last_action: 'EEG Pattern Analysis', performance: 0.94 },
    { name: 'Qubit', role: 'Quantum-Dev', status: 'working', last_action: 'VQE Optimization', performance: 0.97 },
    { name: 'Echo', role: 'Data-Scientist', status: 'working', last_action: 'Resonance Calibration', performance: 0.96 },
  ]);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <Users className={styles.mainIcon} />
          <div>
            <h3>Virtual Squad Command</h3>
            <span className={styles.subtitle}>Stage 22: Elite Personnel</span>
          </div>
        </div>
        <div className={styles.globalPulse}>
          <Activity size={14} className={styles.pulseIcon} />
          <span>SQUAD SYNC: 98.4%</span>
        </div>
      </div>

      <div className={styles.grid}>
        {employees.map((emp) => (
          <motion.div 
            key={emp.role}
            className={styles.card}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
          >
            <div className={styles.cardHeader}>
              <div className={styles.roleBadge}>
                {emp.role === 'Architect' && <Cpu size={12} />}
                {emp.role === 'SecOps' && <Shield size={12} />}
                {emp.role === 'Neuro-Scientist' && <Brain size={12} />}
                {emp.role === 'Quantum-Dev' && <Zap size={12} />}
                <span>{emp.role}</span>
              </div>
              <div className={`${styles.statusDot} ${styles[emp.status]}`}>
                <Circle size={8} fill="currentColor" />
              </div>
            </div>

            <div className={styles.body}>
              <div className={styles.name}>{emp.name}</div>
              <div className={styles.action}>
                <Terminal size={10} className={styles.terminalIcon} />
                <span>{emp.last_action || 'Awaiting orders...'}</span>
              </div>
            </div>

            <div className={styles.footer}>
              <div className={styles.perfBar}>
                <div 
                  className={styles.perfProgress} 
                  style={{ width: `${emp.performance * 100}%` }}
                />
              </div>
              <span className={styles.perfText}>{(emp.performance * 100).toFixed(0)}% EFF</span>
            </div>
          </motion.div>
        ))}
      </div>
      
      <div className={styles.overlay} />
    </div>
  );
};

export default SquadDashboard;
