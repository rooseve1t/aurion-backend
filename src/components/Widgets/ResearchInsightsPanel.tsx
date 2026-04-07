import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ResearchInsight {
  id: string;
  title: string;
  content: string;
  created_at: string;
  importance: number;
}

const API_BASE = (import.meta as any).env?.VITE_API_URL || '';

export function ResearchInsightsPanel() {
  const [insights, setInsights] = useState<ResearchInsight[]>([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [triggering, setTriggering] = useState(false);

  const fetchInsights = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token') || '';
      const res = await fetch(`${API_BASE}/api/v1/jarvis/research/insights?limit=10`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        setInsights(data.insights || []);
      }
    } catch (e) {
      console.error('Failed to fetch insights:', e);
    }
    setLoading(false);
  };

  const triggerResearch = async () => {
    setTriggering(true);
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token') || '';
      await fetch(`${API_BASE}/api/v1/jarvis/research/trigger`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
      setTimeout(fetchInsights, 3000);
    } catch {}
    setTriggering(false);
  };

  useEffect(() => { fetchInsights(); }, []);

  return (
    <div style={{
      background: 'rgba(2, 8, 23, 0.8)',
      border: '1px solid rgba(139, 92, 246, 0.3)',
      borderRadius: '12px',
      padding: '16px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div>
          <h3 style={{ color: '#8b5cf6', fontSize: '13px', fontWeight: 700, letterSpacing: '0.1em' }}>
            🔍 Пассивный ресёрч
          </h3>
          <p style={{ color: '#64748b', fontSize: '10px' }}>
            JARVIS исследует темы из ваших разговоров
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          onClick={triggerResearch}
          disabled={triggering}
          style={{
            background: 'rgba(139, 92, 246, 0.2)',
            border: '1px solid rgba(139, 92, 246, 0.4)',
            borderRadius: '6px',
            padding: '5px 10px',
            color: '#8b5cf6',
            fontSize: '10px',
            cursor: triggering ? 'not-allowed' : 'pointer',
          }}
        >
          {triggering ? '...' : '▶ Запустить'}
        </motion.button>
      </div>

      {loading ? (
        <div style={{ color: '#64748b', fontSize: '11px', textAlign: 'center', padding: '20px' }}>
          Загрузка инсайтов...
        </div>
      ) : insights.length === 0 ? (
        <div style={{ color: '#64748b', fontSize: '11px', textAlign: 'center', padding: '20px' }}>
          Инсайтов пока нет. JARVIS начнёт исследование автоматически.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '300px', overflowY: 'auto' }}>
          {insights.map(insight => (
            <motion.div
              key={insight.id}
              style={{
                background: 'rgba(139, 92, 246, 0.05)',
                border: '1px solid rgba(139, 92, 246, 0.15)',
                borderRadius: '8px',
                padding: '10px',
                cursor: 'pointer',
              }}
              onClick={() => setExpanded(expanded === insight.id ? null : insight.id)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div style={{ fontSize: '11px', color: '#c4b5fd', fontWeight: 600 }}>
                  {insight.title || 'Авто-инсайт'}
                </div>
                <span style={{ fontSize: '9px', color: '#64748b' }}>
                  {insight.created_at ? new Date(insight.created_at).toLocaleDateString('ru') : ''}
                </span>
              </div>
              <AnimatePresence>
                {expanded === insight.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    style={{ overflow: 'hidden' }}
                  >
                    <div style={{
                      marginTop: '8px',
                      fontSize: '10px',
                      color: '#94a3b8',
                      lineHeight: '1.5',
                      borderTop: '1px solid rgba(139, 92, 246, 0.1)',
                      paddingTop: '8px',
                    }}>
                      {insight.content}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ResearchInsightsPanel;
