import { create } from 'zustand';

export interface AgentDeployStatus {
  role: string;
  name: string;
  description: string;
  status: 'idle' | 'deploying' | 'working' | 'complete' | 'failed';
  output: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface HousePartySessionData {
  session_id: string;
  user_id: string;
  goal: string;
  status: 'deploying' | 'complete' | 'failed';
  agent_statuses: Record<string, AgentDeployStatus>;
  final_report: string | null;
  started_at: string;
  completed_at: string | null;
}

interface HousePartyState {
  sessionId: string | null;
  goal: string;
  sessionData: HousePartySessionData | null;
  isActivating: boolean;
  error: string | null;
  activate: (goal: string) => Promise<string | null>;
  updateAgentStatus: (role: string, status: Partial<AgentDeployStatus>) => void;
  setFinalReport: (report: string) => void;
  setComplete: () => void;
  reset: () => void;
}

const API_BASE = (import.meta as any).env?.VITE_API_URL || '';

export const useHousePartyStore = create<HousePartyState>((set, get) => ({
  sessionId: null,
  goal: '',
  sessionData: null,
  isActivating: false,
  error: null,

  activate: async (goal: string) => {
    set({ isActivating: true, error: null });
    try {
      const token = localStorage.getItem('access_token') || localStorage.getItem('token') || '';
      const res = await fetch(`${API_BASE}/api/v1/jarvis/house-party/activate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ goal }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const sessionId = data.session_id;

      // Initialize session data
      const initialAgents: Record<string, AgentDeployStatus> = {};
      const roles = [
        { role: 'cto', name: 'Alpha — CTO', description: 'Стратегия и архитектура' },
        { role: 'tech_lead', name: 'Sigma — Tech Lead', description: 'Планирование и декомпозиция' },
        { role: 'senior_dev', name: 'Lux — Developer', description: 'Реализация' },
        { role: 'qa', name: 'Omega — QA', description: 'Тестирование' },
        { role: 'security', name: 'Sentinel — Security', description: 'Безопасность' },
        { role: 'devops', name: 'Flux — DevOps', description: 'Инфраструктура' },
        { role: 'analyst', name: 'Nexus — Analyst', description: 'Аналитика' },
        { role: 'researcher', name: 'Echo — Researcher', description: 'Исследования' },
      ];
      roles.forEach(r => {
        initialAgents[r.role] = { ...r, status: 'idle', output: '', started_at: null, completed_at: null };
      });

      set({
        sessionId,
        goal,
        isActivating: false,
        sessionData: {
          session_id: sessionId,
          user_id: '',
          goal,
          status: 'deploying',
          agent_statuses: initialAgents,
          final_report: null,
          started_at: new Date().toISOString(),
          completed_at: null,
        },
      });
      return sessionId;
    } catch (e: any) {
      set({ isActivating: false, error: e.message });
      return null;
    }
  },

  updateAgentStatus: (role, updates) => set((state) => {
    if (!state.sessionData) return state;
    return {
      sessionData: {
        ...state.sessionData,
        agent_statuses: {
          ...state.sessionData.agent_statuses,
          [role]: { ...state.sessionData.agent_statuses[role], ...updates },
        },
      },
    };
  }),

  setFinalReport: (report) => set((state) => ({
    sessionData: state.sessionData ? { ...state.sessionData, final_report: report, status: 'complete' } : null,
  })),

  setComplete: () => set((state) => ({
    sessionData: state.sessionData ? { ...state.sessionData, status: 'complete', completed_at: new Date().toISOString() } : null,
  })),

  reset: () => set({ sessionId: null, goal: '', sessionData: null, isActivating: false, error: null }),
}));
