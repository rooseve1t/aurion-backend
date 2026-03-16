import { create } from 'zustand'
import type { Agent, AgentTask } from '@/types'
import { agentsService } from '@/services/agents'
import toast from 'react-hot-toast'

interface TasksState {
  agents: Agent[]
  tasks: AgentTask[]
  total: number
  loading: boolean
  fetchAgents: () => Promise<void>
  fetchTasks: (status?: string) => Promise<void>
  createTask: (type: string, input: Record<string, unknown>) => Promise<void>
  cancelTask: (id: number) => Promise<void>
  swarm: (goal: string) => Promise<void>
}

export const useTasksStore = create<TasksState>()((set, get) => ({
  agents: [],
  tasks: [],
  total: 0,
  loading: false,

  fetchAgents: async () => {
    const agents = await agentsService.list()
    set({ agents })
  },

  fetchTasks: async (status) => {
    set({ loading: true })
    try {
      const { tasks, total } = await agentsService.getTasks(status)
      set({ tasks, total })
    } finally {
      set({ loading: false })
    }
  },

  createTask: async (type, input) => {
    await agentsService.createTask(type, input)
    toast.success('Задача запущена')
    await get().fetchTasks()
  },

  cancelTask: async (id) => {
    await agentsService.cancelTask(id)
    toast.success('Задача отменена')
    await get().fetchTasks()
  },

  swarm: async (goal) => {
    const result = await agentsService.swarm(goal)
    toast.success(`Роевая задача: ${result.subtasks_created} подзадач`)
    await get().fetchTasks()
  },
}))
