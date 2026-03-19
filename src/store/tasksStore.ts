import { create } from 'zustand'
import type { Agent, AgentTask } from '@/types'
import { agentsService } from '@/services/agents'
import { useUIStore } from './uiStore'

interface TasksState {
  agents: Agent[]
  tasks: AgentTask[]
  total: number
  loading: boolean
  fetchAgents: () => Promise<void>
  fetchTasks: () => Promise<void>
  createTask: (action: string, parameters: Record<string, unknown>) => Promise<void>
  cancelTask: (id: number) => Promise<void>
  swarm: (goal: string) => Promise<void>
}

export const useTasksStore = create<TasksState>()((set, get) => ({
  agents: [],
  tasks: [],
  total: 0,
  loading: false,

  fetchAgents: async () => {
    const agents = await agentsService.listAgents()
    set({ agents })
  },

  fetchTasks: async () => {
    set({ loading: true })
    try {
      const tasks = await agentsService.listTasks()
      set({ tasks, total: tasks.length })
    } finally {
      set({ loading: false })
    }
  },

  createTask: async (action, parameters) => {
    let agents = get().agents
    if (agents.length === 0) {
      agents = await agentsService.listAgents()
      set({ agents })
    }
    if (agents.length === 0) {
      useUIStore.getState().showToast('Сначала создайте агента', 'warning')
      return
    }
    await agentsService.createTask(agents[0].id, action, parameters)
    useUIStore.getState().showToast('Задача запущена', 'success')
    await get().fetchTasks()
  },

  cancelTask: async (id) => {
    await agentsService.cancelTask(id)
    useUIStore.getState().showToast('Задача отменена', 'success')
    await get().fetchTasks()
  },

  swarm: async (goal) => {
    await agentsService.runSwarm(goal)
    useUIStore.getState().showToast('Рой агентов запущен', 'success')
    await get().fetchTasks()
  },
}))
