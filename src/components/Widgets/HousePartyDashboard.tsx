import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useHousePartyStore, AgentDeployStatus } from '../../store/housePartyStore';

const ROLE_ICONS: Record<string, string> = {
  cto: '👑', tech_lead: '⚡', senior_dev: '💻', qa: '🔬',
  security: '🛡️', devops: '🚀', analyst: '📊', researcher: '🔭',
};

function AgentCard({ agent, index }: { agent: AgentDeployStatus; index: number }) {
  const statusColors: Record<string, string> = {
    idle: '#64748b',
    deploying: '#f59e0b',
    working: '#06b6d4',
    complete: '#22c55e',
    failed: '#ef4444',
  };
  const statusLabels: Record<string, string> = {
    idle: 'Ожидание',
    deploying: 'Развёртывание...',
    working: 'Работает...',
    complete: 'Завершено',
    failed: 'Ошибка',
  };

  const color = statusColors[agent.status] || '#64748b';
  const icon = ROLE_ICONS[agent.role] || '🤖';

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.08, duration: 0.4, ease: 'easeOut' }}
      style={{
        background: 'rgba(2, 8, 23, 0.8)',
        border: `1px solid ${color}40`,
        borderRadius: '8px',
        padding: '12px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Glow line at top */}
      <motion.div
        animate={agent.status === 'working' ? { opacity: [0.3, 1, 0.3] } : { opacity: 0.4 }}
        transition={{ duration: 1.5, repeat: Infinity }}
        style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '2px', background: color }}
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
        <span style={{ fontSize: '18px' }}>{icon}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: '#e2e8f0' }}>{agent.name}</div>
          <div style={{ fontSize: '9px', color: '#64748b' }}>{agent.description}</div>
        </div>
      </div>

      {/* Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
        <motion.div
          animate={agent.status === 'working' ? { opacity: [1, 0, 1] } : {}}
          transition={{ duration: 0.8, repeat: Infinity }}
          style={{ width: '6px', height: '6px', borderRadius: '50%', background: color, flexShrink: 0 }}
        />
        <span style={{ fontSize: '9px', color, fontWeight: 600 }}>{statusLabels[agent.status]}</span>
      </div>

      {/* Output preview */}
      {agent.output && (
        <div style={{
          fontSize: '9px',
          color: '#94a3b8',
          lineHeight: '1.4',
          maxHeight: '40px',
          overflow: 'hidden',
          borderTop: '1px solid rgba(255,255,255,0.05)',
          paddingTop: '4px',
          marginTop: '4px',
        }}>
          {agent.output.slice(0, 120)}{agent.output.length > 120 ? '...' : ''}
        </div>
      )}
    </motion.div>
  );
}

export function HousePartyDashboard() {
  const { sessionData, isActivating, error, activate, reset } = useHousePartyStore();
  const [goalInput, setGoalInput] = useState('');
  const [showReport, setShowReport] = useState(false);

  // Listen to WS messages
  useEffect(() => {
    const { updateAgentStatus, setFinalReport, setComplete } = useHousePartyStore.getState();
    const handleMessage = (e: MessageEvent) => {
      try {
        const data = typeof e.data === 'string' ? JSON.parse(e.data) : e.data;
        if (data?.type === 'house_party_agent_update') {
          updateAgentStatus(data.role, {
            status: data.status,
            output: data.output || '',
          });
        }
        if (data?.type === 'house_party_complete') {
          setFinalReport(data.final_report || '');
          setComplete();
          setShowReport(true);
        }
      } catch {}
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const handleActivate = async () => {
    if (!goalInput.trim()) return;
    await activate(goalInput.trim());
    setGoalInput('');
  };

  const completedCount = sessionData
    ? Object.values(sessionData.agent_statuses).filter(a => a.status === 'complete').length
    : 0;
  const totalAgents = 8;
  const progressPct = sessionData ? (completedCount / totalAgents) * 100 : 0;

  if (!sessionData) {
    return (
      <div style={{
        background: 'rgba(2, 8, 23, 0.8)',
        border: '1px solid rgba(239, 68, 68, 0.3)',
        borderRadius: '12px',
        padding: '20px',
      }}>
        <div style={{ marginBottom: '16px' }}>
          <h3 style={{
            color: '#ef4444',
            fontSize: '14px',
            fontWeight: 700,
            letterSpacing: '0.15em',
            textTransform: 'uppercase',
            marginBottom: '4px',
          }}>
            🎉 House Party Protocol
          </h3>
          <p style={{ color: '#64748b', fontSize: '11px' }}>
            Развёртывает всех 8 агентов одновременно — как в Iron Man 3
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            value={goalInput}
            onChange={e => setGoalInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleActivate()}
            placeholder="Введите цель..."
            style={{
              flex: 1,
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '6px',
              padding: '8px 12px',
              color: '#e2e8f0',
              fontSize: '12px',
              outline: 'none',
            }}
          />
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={handleActivate}
            disabled={isActivating || !goalInput.trim()}
            style={{
              background: isActivating ? 'rgba(239, 68, 68, 0.3)' : 'rgba(239, 68, 68, 0.8)',
              border: '1px solid #ef4444',
              borderRadius: '6px',
              padding: '8px 16px',
              color: 'white',
              fontSize: '11px',
              fontWeight: 700,
              cursor: isActivating ? 'not-allowed' : 'pointer',
              letterSpacing: '0.05em',
            }}
          >
            {isActivating ? 'ЗАПУСК...' : 'АКТИВИРОВАТЬ'}
          </motion.button>
        </div>

        {error && (
          <p style={{ color: '#ef4444', fontSize: '10px', marginTop: '8px' }}>Ошибка: {error}</p>
        )}
      </div>
    );
  }

  return (
    <div style={{
      background: 'rgba(2, 8, 23, 0.9)',
      border: '1px solid rgba(239, 68, 68, 0.4)',
      borderRadius: '12px',
      padding: '16px',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div>
          <h3 style={{ color: '#ef4444', fontSize: '13px', fontWeight: 700, letterSpacing: '0.1em' }}>
            🎉 HOUSE PARTY PROTOCOL
          </h3>
          <p style={{ color: '#94a3b8', fontSize: '10px' }}>
            {sessionData.goal.slice(0, 60)}{sessionData.goal.length > 60 ? '...' : ''}
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <span style={{
            fontSize: '12px',
            fontWeight: 700,
            color: sessionData.status === 'complete' ? '#22c55e' : '#f59e0b',
          }}>
            {completedCount}/{totalAgents}
          </span>
          <br />
          <span style={{ fontSize: '9px', color: '#64748b' }}>агентов</span>
        </div>
      </div>

      {/* Progress bar */}
      <div style={{ height: '3px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginBottom: '14px' }}>
        <motion.div
          animate={{ width: `${progressPct}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{ height: '100%', background: 'linear-gradient(90deg, #ef4444, #f59e0b)', borderRadius: '2px' }}
        />
      </div>

      {/* Agent grid - 4x2 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
        {Object.values(sessionData.agent_statuses).map((agent, i) => (
          <AgentCard key={agent.role} agent={agent} index={i} />
        ))}
      </div>

      {/* Final Report */}
      <AnimatePresence>
        {showReport && sessionData.final_report && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            style={{
              marginTop: '12px',
              borderTop: '1px solid rgba(34, 197, 94, 0.3)',
              paddingTop: '12px',
            }}
          >
            <h4 style={{ color: '#22c55e', fontSize: '11px', fontWeight: 700, marginBottom: '8px', letterSpacing: '0.1em' }}>
              ✅ ФИНАЛЬНЫЙ ОТЧЁТ
            </h4>
            <div style={{
              color: '#94a3b8',
              fontSize: '11px',
              lineHeight: '1.6',
              maxHeight: '200px',
              overflowY: 'auto',
              whiteSpace: 'pre-wrap',
              background: 'rgba(255,255,255,0.03)',
              padding: '10px',
              borderRadius: '6px',
              border: '1px solid rgba(34, 197, 94, 0.15)',
            }}>
              {sessionData.final_report}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Reset button */}
      {sessionData.status === 'complete' && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={reset}
          style={{
            marginTop: '10px',
            background: 'transparent',
            border: '1px solid rgba(100, 116, 139, 0.4)',
            borderRadius: '6px',
            padding: '6px 12px',
            color: '#64748b',
            fontSize: '10px',
            cursor: 'pointer',
            width: '100%',
          }}
        >
          Сбросить протокол
        </motion.button>
      )}
    </div>
  );
}

export default HousePartyDashboard;
