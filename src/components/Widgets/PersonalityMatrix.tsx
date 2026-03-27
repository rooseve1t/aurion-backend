import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  User, 
  Shield, 
  Cpu, 
  Zap, 
  MessageSquare, 
  Heart, 
  Activity,
  ChevronRight,
  Flame
} from 'lucide-react';
import styles from './PersonalityMatrix.module.css';

interface Trait {
  id: string;
  name: string;
  value: number;
  icon: React.ElementType;
  color: string;
}

const PersonalityMatrix: React.FC = () => {
  const [traits, setTraits] = useState<Trait[]>([
    { id: 'sarcastic', name: 'Sarcastic', value: 85, icon: MessageSquare, color: '#00f2ff' },
    { id: 'caring', name: 'Caring', value: 75, icon: Heart, color: '#ff0055' },
    { id: 'professional', name: 'Professional', value: 90, icon: Shield, color: '#00ff95' },
    { id: 'witty', name: 'Witty', value: 80, icon: Zap, color: '#fbff00' },
    { id: 'loyal', name: 'Loyal', value: 100, icon: User, color: '#ffffff' },
    { id: 'protective', name: 'Protective', value: 95, icon: Activity, color: '#ff8800' },
  ]);

  const [activeTrait, setActiveTrait] = useState<string | null>(null);

  const handleTraitChange = (id: string, newValue: number) => {
    setTraits(prev => prev.map(t => t.id === id ? { ...t, value: newValue } : t));
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <Cpu className={styles.mainIcon} />
          <div>
            <h3>Neural Personality Matrix</h3>
            <span className={styles.subtitle}>Stage 22: Character Synthesis</span>
          </div>
        </div>
        <div className={styles.statusBadge}>ACTIVE</div>
      </div>

      <div className={styles.matrixGrid}>
        {traits.map((trait) => (
          <motion.div 
            key={trait.id}
            className={`${styles.traitCard} ${activeTrait === trait.id ? styles.active : ''}`}
            whileHover={{ scale: 1.02 }}
            onMouseEnter={() => setActiveTrait(trait.id)}
            onMouseLeave={() => setActiveTrait(null)}
          >
            <div className={styles.traitHeader}>
              <trait.icon size={18} style={{ color: trait.color }} />
              <span className={styles.traitName}>{trait.name}</span>
              <span className={styles.traitValue}>{trait.value}%</span>
            </div>
            
            <div className={styles.progressTrack}>
              <motion.div 
                className={styles.progressBar}
                initial={{ width: 0 }}
                animate={{ width: `${trait.value}%` }}
                style={{ 
                  backgroundColor: trait.color,
                  boxShadow: `0 0 10px ${trait.color}44`
                }}
              />
            </div>

            <div className={styles.controls}>
              <button 
                className={styles.adjustBtn}
                onClick={() => handleTraitChange(trait.id, Math.max(0, trait.value - 5))}
              >-</button>
              <button 
                className={styles.adjustBtn}
                onClick={() => handleTraitChange(trait.id, Math.min(100, trait.value + 5))}
              >+</button>
            </div>
          </motion.div>
        ))}
      </div>

      <div className={styles.footer}>
        <div className={styles.moodIndicator}>
          <Flame size={16} />
          <span>Current Resonance: <strong>SYNCHRONIZED</strong></span>
        </div>
        <button className={styles.deployBtn}>
          <span>Apply Personality Delta</span>
          <ChevronRight size={16} />
        </button>
      </div>
      
      <div className={styles.glassNoise} />
    </div>
  );
};

export default PersonalityMatrix;
