import { api } from './api'
import type { Agent, AgentTask } from '@/types'

export const agentsService = {
  async listAgents(): Promise<Agent[]> {
    const { data } = await api.get<Agent[]>('/agents/')
    return data
  },

  async createAgent(payload: { name: string; agent_type: string; config: Record<string, unknown> }): Promise<Agent> {
    const { data } = await api.post<Agent>('/agents/', payload)
    return data
  },

  async deleteAgent(id: string | number): Promise<void> {
    await api.delete(`/agents/${id}`)
  },

  async listTasks(): Promise<AgentTask[]> {
    const { data } = await api.get<AgentTask[]>('/agents/tasks')
    return data
  },

  async createTask(agentId: string | number, action: string, parameters: Record<string, unknown> = {}): Promise<AgentTask> {
    const { data } = await api.post<AgentTask>('/agents/tasks', {
      agent_id: String(agentId),
      action,
      parameters,
    })
    return data
  },

  async cancelTask(id: string | number): Promise<void> {
    await api.post(`/agents/tasks/${id}/cancel`)
  },

  async runSwarm(goal: string): Promise<{ task_id: string }> {
    const { data } = await api.post('/agents/swarm', { goal })
    return data
  },
}
