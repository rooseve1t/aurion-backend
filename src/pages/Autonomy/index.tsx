import { useEffect, useState } from 'react'
import { Cpu, Plus, X, Play, ChevronDown, ChevronUp, Zap } from 'lucide-react'
import { useTasksStore } from '@/store/tasksStore'
import { agentsService } from '@/services/agents'
import type { AgentType } from '@/types'
import { formatDate } from '@/utils'
import toast from 'react-hot-toast'

const STATUS_COLORS: Record<string, string> = {
  pending:     'text-amber  border-amber/30  bg-amber/5',
  in_progress: 'text-cyan   border-cyan/30   bg-cyan/5',
  completed:   'text-emerald border-emerald/30 bg-emerald/5',
  failed:      'text-danger  border-danger/30  bg-danger/5',
  cancelled:   'text-white/30 border-white/10  bg-white/3',
}

const AGENT_TYPES: { value: AgentType; label: string }[] = [
  { value: 'financial',  label: 'Финансовый' },
  { value: 'smarthome',  label: 'Умный дом'  },
  { value: 'osint',      label: 'OSINT'       },
  { value: 'memory',     label: 'Память'      },
]

const TASK_TYPES: Record<AgentType, string[]> = {
  financial:  ['analyze_spending', 'financial_tips'],
  smarthome:  ['collect_device_stats', 'optimize_home'],
  osint:      ['search_ip', 'search_email'],
  memory:     ['recall_memory', 'memory_summary'],
}

export default function AutonomyPage() {
  const { agents, tasks, loading, fetchAgents, fetchTasks, createTask, cancelTask, swarm } = useTasksStore()
  const [showCreateAgent, setShowCreateAgent] = useState(false)
  const [showSwarm, setShowSwarm] = useState(false)
  const [agentName, setAgentName] = useState('')
  const [agentType, setAgentType] = useState<AgentType>('financial')
  const [taskType, setTaskType] = useState('analyze_spending')
  const [swarmGoal, setSwarmGoal] = useState('')
  const [expandedTask, setExpandedTask] = useState<number | null>(null)

  useEffect(() => {
    fetchAgents()
    fetchTasks()
    const interval = setInterval(() => fetchTasks(), 10000)
    return () => clearInterval(interval)
  }, [])

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await agentsService.create({ name: agentName, type: agentType, config: {} })
      toast.success('Агент создан')
      setAgentName('')
      setShowCreateAgent(false)
      fetchAgents()
    } catch { toast.error('Ошибка создания агента') }
  }

  const handleCreateTask = async () => {
    await createTask(taskType, {})
  }

  const handleSwarm = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!swarmGoal.trim()) return
    await swarm(swarmGoal)
    setSwarmGoal('')
    setShowSwarm(false)
  }

  const inputCls = 'w-full bg-surface border border-cyan/20 rounded px-3 py-2 text-sm text-white placeholder-white/30 focus:outline-none focus:border-cyan/40'

  return (
    <div className="p-4 max-w-4xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Cpu size={20} className="text-purple" />
          <div>
            <div className="font-bold text-sm tracking-wider">АВТОНОМИЯ</div>
            <div className="text-[10px] text-white/30">{agents.length} агентов · {tasks.length} задач</div>
          </div>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowSwarm(!showSwarm)}
            className="flex items-center gap-1 px-3 py-1.5 bg-amber/10 hover:bg-amber/20 border border-amber/30 text-amber text-xs rounded transition-all">
            <Zap size={12} /> Рой
          </button>
          <button onClick={() => setShowCreateAgent(!showCreateAgent)}
            className="flex items-center gap-1 px-3 py-1.5 bg-purple/10 hover:bg-purple/20 border border-purple/30 text-purple text-xs rounded transition-all">
            <Plus size={12} /> Агент
          </button>
        </div>
      </div>

      {/* Swarm form */}
      {showSwarm && (
        <form onSubmit={handleSwarm} className="bg-card border border-amber/20 rounded-lg p-4 space-y-3 animate-fade-in">
          <div className="text-xs text-amber font-bold tracking-wider">РОЕВАЯ ЗАДАЧА</div>
          <input value={swarmGoal} onChange={(e) => setSwarmGoal(e.target.value)}
            placeholder="Цель: оптимизировать расходы и дом..." className={inputCls} />
          <div className="flex gap-2">
            <button type="submit" className="px-4 py-1.5 bg-amber/20 border border-amber/40 text-amber text-xs rounded">Запустить</button>
            <button type="button" onClick={() => setShowSwarm(false)} className="px-4 py-1.5 text-white/30 text-xs">Отмена</button>
          </div>
        </form>
      )}

      {/* Create agent form */}
      {showCreateAgent && (
        <form onSubmit={handleCreateAgent} className="bg-card border border-purple/20 rounded-lg p-4 space-y-3 animate-fade-in">
          <div className="text-xs text-purple font-bold tracking-wider">НОВЫЙ АГЕНТ</div>
          <input value={agentName} onChange={(e) => setAgentName(e.target.value)}
            placeholder="Название агента" className={inputCls} required />
          <select value={agentType} onChange={(e) => { setAgentType(e.target.value as AgentType); setTaskType(TASK_TYPES[e.target.value as AgentType][0]) }}
            className={inputCls}>
            {AGENT_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
          </select>
          <div className="flex gap-2">
            <button type="submit" className="px-4 py-1.5 bg-purple/20 border border-purple/40 text-purple text-xs rounded">Создать</button>
            <button type="button" onClick={() => setShowCreateAgent(false)} className="text-white/30 text-xs px-4">Отмена</button>
          </div>
        </form>
      )}

      {/* Quick task */}
      {agents.length > 0 && (
        <div className="bg-card border border-cyan/15 rounded-lg p-4 space-y-3">
          <div className="text-xs text-cyan/60 tracking-wider font-bold">БЫСТРАЯ ЗАДАЧА</div>
          <div className="flex gap-2">
            <select value={taskType} onChange={(e) => setTaskType(e.target.value)}
              className={inputCls + ' flex-1'}>
              {Object.values(TASK_TYPES).flat().map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <button onClick={handleCreateTask}
              className="flex items-center gap-1 px-4 py-2 bg-cyan/10 border border-cyan/30 text-cyan text-xs rounded hover:bg-cyan/20 transition-all">
              <Play size={12} /> Запуск
            </button>
          </div>
        </div>
      )}

      {/* Agents list */}
      {agents.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs text-white/30 tracking-wider">АГЕНТЫ ({agents.length})</div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {agents.map((a) => (
              <div key={a.id} className="bg-card border border-white/8 rounded-lg p-3 flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${a.is_active ? 'bg-emerald' : 'bg-white/20'}`} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm truncate">{a.name}</div>
                  <div className="text-[10px] text-white/30">{a.type}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tasks */}
      <div className="space-y-2">
        <div className="text-xs text-white/30 tracking-wider">ЗАДАЧИ</div>
        {loading ? (
          <div className="space-y-2">
            {[...Array(3)].map((_, i) => <div key={i} className="h-14 bg-card border border-white/5 rounded animate-pulse" />)}
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8 text-white/20 text-sm">Нет задач</div>
        ) : (
          <div className="space-y-2">
            {tasks.map((task) => (
              <div key={task.id} className="bg-card border border-white/8 rounded-lg overflow-hidden">
                <div className="p-3 flex items-center gap-3 cursor-pointer"
                  onClick={() => setExpandedTask(expandedTask === task.id ? null : task.id)}>
                  <span className={`text-[10px] px-2 py-0.5 rounded border ${STATUS_COLORS[task.status] ?? ''}`}>
                    {task.status}
                  </span>
                  <span className="flex-1 text-sm text-white/80 truncate">{task.type}</span>
                  <span className="text-[10px] text-white/30">{formatDate(task.created_at)}</span>
                  {task.status === 'pending' && (
                    <button onClick={(e) => { e.stopPropagation(); cancelTask(task.id) }}
                      className="text-white/20 hover:text-danger transition-colors">
                      <X size={14} />
                    </button>
                  )}
                  {expandedTask === task.id ? <ChevronUp size={14} className="text-white/30" /> : <ChevronDown size={14} className="text-white/30" />}
                </div>
                {expandedTask === task.id && (
                  <div className="px-3 pb-3 border-t border-white/5 pt-2 space-y-1">
                    {task.output_data && (
                      <pre className="text-[10px] text-white/50 overflow-auto max-h-32 bg-surface rounded p-2">
                        {JSON.stringify(task.output_data, null, 2)}
                      </pre>
                    )}
                    {task.error_message && (
                      <div className="text-[10px] text-danger">{task.error_message}</div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
