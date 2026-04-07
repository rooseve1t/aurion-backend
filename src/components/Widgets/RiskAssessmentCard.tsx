import React from 'react';
import { motion } from 'framer-motion';

interface RiskReport {
  action_id: string;
  action_type: string;
  risk_level: number;
  risk_label: string;
  estimated_duration_sec: number;
  affected_subsystems: string[];
  potential_side_effects: string[];
  recommendation: string;
  auto_approve: boolean;
  warning_message: string;
}

interface RiskAssessmentCardProps {
  riskReport: RiskReport;
  onConfirm: () => void;
  onAbort: () => void;
  actionDescription?: string;
}

function RiskBadge({ level, label }: { level: number; label: string }) {
  const color = level >= 8 ? '#ef4444' : level >= 6 ? '#f97316' : level >= 4 ? '#f59e0b' : '#22c55e';
  const bg = level >= 8 ? 'rgba(239,68,68,0.15)' : level >= 6 ? 'rgba(249,115,22,0.15)' : level >= 4 ? 'rgba(245,158,11,0.15)' : 'rgba(34,197,94,0.15)';

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      background: bg,
      border: `1px solid ${color}40`,
      borderRadius: '8px',
      padding: '8px 14px',
    }}>
      <span style={{ fontSize: '22px', fontWeight: 900, color, fontFamily: 'monospace' }}>{level}</span>
      <div>
        <div style={{ fontSize: '8px', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Уровень риска</div>
        <div style={{ fontSize: '12px', fontWeight: 700, color }}>{label}</div>
      </div>
    </div>
  );
}

export function RiskAssessmentCard({ riskReport, onConfirm, onAbort, actionDescription }: RiskAssessmentCardProps) {
  const formatDuration = (sec: number) => {
    if (sec < 60) return `${sec}с`;
    return `${Math.floor(sec / 60)}м ${sec % 60}с`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      style={{
        background: 'rgba(2, 8, 23, 0.95)',
        border: '1px solid rgba(245, 158, 11, 0.4)',
        borderRadius: '12px',
        padding: '16px',
        maxWidth: '420px',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
        <span style={{ fontSize: '18px' }}>⚠️</span>
        <div>
          <h4 style={{ color: '#f59e0b', fontSize: '12px', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            Оценка рисков JARVIS
          </h4>
          {actionDescription && (
            <p style={{ color: '#94a3b8', fontSize: '10px' }}>{actionDescription}</p>
          )}
        </div>
      </div>

      {/* Warning message */}
      {riskReport.warning_message && (
        <div style={{
          background: 'rgba(245, 158, 11, 0.1)',
          border: '1px solid rgba(245, 158, 11, 0.2)',
          borderRadius: '6px',
          padding: '8px 12px',
          marginBottom: '12px',
          fontSize: '11px',
          color: '#fbbf24',
          fontStyle: 'italic',
        }}>
          "{riskReport.warning_message}"
        </div>
      )}

      {/* Risk badge + duration */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '12px', alignItems: 'flex-start' }}>
        <RiskBadge level={riskReport.risk_level} label={riskReport.risk_label} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '9px', color: '#64748b', marginBottom: '2px' }}>ОЖИДАЕМОЕ ВРЕМЯ</div>
          <div style={{ fontSize: '14px', fontWeight: 700, color: '#e2e8f0', fontFamily: 'monospace' }}>
            {formatDuration(riskReport.estimated_duration_sec)}
          </div>
        </div>
      </div>

      {/* Affected subsystems */}
      {riskReport.affected_subsystems.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontSize: '9px', color: '#64748b', textTransform: 'uppercase', marginBottom: '5px', letterSpacing: '0.1em' }}>
            Затронутые подсистемы
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {riskReport.affected_subsystems.map(s => (
              <span key={s} style={{
                background: 'rgba(6, 182, 212, 0.1)',
                border: '1px solid rgba(6, 182, 212, 0.3)',
                borderRadius: '4px',
                padding: '2px 8px',
                fontSize: '9px',
                color: '#06b6d4',
              }}>
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Side effects */}
      {riskReport.potential_side_effects.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <div style={{ fontSize: '9px', color: '#64748b', textTransform: 'uppercase', marginBottom: '5px', letterSpacing: '0.1em' }}>
            Возможные побочные эффекты
          </div>
          {riskReport.potential_side_effects.map(e => (
            <div key={e} style={{ fontSize: '10px', color: '#94a3b8', display: 'flex', gap: '6px', marginBottom: '2px' }}>
              <span style={{ color: '#f59e0b' }}>•</span> {e}
            </div>
          ))}
        </div>
      )}

      {/* Recommendation */}
      <div style={{
        background: 'rgba(255,255,255,0.03)',
        border: '1px solid rgba(255,255,255,0.07)',
        borderRadius: '6px',
        padding: '8px 10px',
        marginBottom: '14px',
        fontSize: '10px',
        color: '#cbd5e1',
      }}>
        <strong style={{ color: '#94a3b8' }}>Рекомендация: </strong>
        {riskReport.recommendation}
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', gap: '8px' }}>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onConfirm}
          style={{
            flex: 1,
            background: riskReport.risk_level >= 7 ? 'rgba(239,68,68,0.2)' : 'rgba(34,197,94,0.2)',
            border: `1px solid ${riskReport.risk_level >= 7 ? '#ef4444' : '#22c55e'}`,
            borderRadius: '6px',
            padding: '8px',
            color: riskReport.risk_level >= 7 ? '#ef4444' : '#22c55e',
            fontSize: '11px',
            fontWeight: 700,
            cursor: 'pointer',
            letterSpacing: '0.05em',
          }}
        >
          ✓ ПОДТВЕРДИТЬ
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onAbort}
          style={{
            flex: 1,
            background: 'rgba(100, 116, 139, 0.1)',
            border: '1px solid rgba(100, 116, 139, 0.3)',
            borderRadius: '6px',
            padding: '8px',
            color: '#64748b',
            fontSize: '11px',
            fontWeight: 700,
            cursor: 'pointer',
            letterSpacing: '0.05em',
          }}
        >
          ✗ ОТМЕНИТЬ
        </motion.button>
      </div>
    </motion.div>
  );
}

export default RiskAssessmentCard;
