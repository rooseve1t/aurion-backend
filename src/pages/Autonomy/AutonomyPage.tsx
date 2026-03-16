import { useState, useEffect } from 'react'
import { Cpu, Plus, Play, X, RefreshCw } from 'lucide-react'
import { agentsService } from '@/services/agents'
import { useToast } from '@/hooks/useToast'
import type { Agent, AgentTask } from '@/types'
import { agentTypeLabel, taskStatusLabel, formatDate } from '@/utils'
import styles from './AutonomyPage.module.css'

const STATUS_COLOR: Record<string, string> = {
  queued:    'var(--text-muted)',
  running:   'var(--cyan)',
  completed: 'var(--green)',
  failed:    'var(--red)',
  cancelled: 'var(--amber)',
}

export function AutonomyPage() {
  const [agents, setAgents]   = useState<Agent[]>([])
  const [tasks, setTasks]     = useState<AgentTask[]>([])
  const [loading, setLoading] = useState(false)
  const [showAdd, setShowAdd] = useState(false)
  const [swarmGoal, setSwarmGoal] = useState('')
  const [newAgent, setNewAgent] = useState({ name: '', agent_type: 'memory' })
  const toast = useToast()

  const refresh = async () => {
    setLoading(true)
    try {
      const [a, t] = await Promise.all([agentsService.listAgents(), agentsService.listTasks()])
      setAgents(a)
      setTasks(t)
    } catch { toast.error('Ошибка загрузки') }
    finally { setLoading(false) }
  }

  useEffect(() => { refresh() }, [])

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const agent = await agentsService.createAgent({ ...newAgent, config: {} })
      setAgents((a) => [...a, agent])
      setShowAdd(false)
      toast.success('Агент создан')
    } catch { toast.error('Ошибка создания агента') }
  }

  const handleRunTask = async (agent: Agent) => {
    try {
      const task = await agentsService.createTask(agent.id, 'default', {})
      setTasks((t) => [task, ...t])
      toast.success(`Задача создана для ${agent.name}`)
    } catch { toast.error('Ошибка запуска') }
  }

  const handleSwarm = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!swarmGoal.trim()) return
    try {
      await agentsService.runSwarm(swarmGoal)
      toast.success('Рой агентов запущен')
      setSwarmGoal('')
      setTimeout(refresh, 2000)
    } catch { toast.error('Ошибка запуска роя') }
  }

  const handleCancel = async (id: number) => {
    try {
      await agentsService.cancelTask(id)
      setTasks((t) => t.map((task) => task.id === id ? { ...task, status: 'cancelled' } : task))
    } catch { toast.error('Ошибка отмены') }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Cpu size={20} color="var(--cyan)" />
          <span className={styles.title}>АГЕНТЫ И ЗАДАЧИ</span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-ghost" onClick={refresh} disabled={loading}>
            <RefreshCw size={14} className={loading ? styles.spinning : ''} />
          </button>
          <button className="btn btn-cyan" onClick={() => setShowAdd(!showAdd)}>
            <Plus size={14} /> АГЕНТ
          </button>
        </div>
      </div>

      {/* Swarm */}
      <div className={styles.swarmPanel}>
        <div className={styles.swarmTitle}>РОЙ АГЕНТОВ</div>
        <form className={styles.swarmForm} onSubmit={handleSwarm}>
          <input className="input" value={swarmGoal}
            onChange={(e) => setSwarmGoal(e.target.value)}
            placeholder="Цель для роя (например: оптимизировать систему)..."
            style={{ flex: 1 }} />
          <button type="submit" className="btn btn-cyan" disabled={!swarmGoal.trim()}>
            <Play size={14} /> ЗАПУСТИТЬ
          </button>
        </form>
      </div>

      {showAdd && (
        <form className={styles.addForm} onSubmit={handleCreateAgent}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label className="label">ИМЯ АГЕНТА</label>
              <input className="input" value={newAgent.name}
                onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })} required />
            </div>
            <div>
              <label className="label">ТИП</label>
              <select className="input" value={newAgent.agent_type}
                onChange={(e) => setNewAgent({ ...newAgent, agent_type: e.target.value })}>
                {Object.entries(agentTypeLabel).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <button type="button" className="btn btn-ghost" onClick={() => setShowAdd(false)}>ОТМЕНА</button>
            <button type="submit" className="btn btn-cyan">СОЗДАТЬ</button>
          </div>
        </form>
      )}

      <div className={styles.body}>
        {/* Agents */}
        <div className={styles.section}>
          <div className={styles.sectionTitle}>АГЕНТЫ ({agents.length})</div>
          {agents.length === 0 && !loading && (
            <div className={styles.empty}>Нет агентов</div>
          )}
          <div className={styles.agentList}>
            {agents.map((agent) => (
              <div key={agent.id} className={styles.agentCard}>
                <div>
                  <div className={styles.agentName}>{agent.name}</div>
                  <div className={styles.agentType}>{agentTypeLabel[agent.agent_type] || agent.agent_type}</div>
                </div>
                <button className="btn btn-cyan"
                  style={{ fontSize: '10px', padding: '4px 10px' }}
                  onClick={() => handleRunTask(agent)}>
                  <Play size={10} /> ЗАПУСК
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Tasks */}
        <div className={styles.section}>
          <div className={styles.sectionTitle}>ЗАДАЧИ ({tasks.length})</div>
          <div className={styles.taskList}>
            {tasks.map((task) => (
              <div key={task.id} className={styles.taskCard} data-testid="task-card">
                <div>
                  <div className={styles.taskAction}>{task.action}</div>
                  <div className={styles.taskMeta}>
                    #{task.id} · {formatDate(task.created_at)}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ color: STATUS_COLOR[task.status] || 'var(--text-muted)', fontSize: '11px' }}>
                    ● {taskStatusLabel[task.status] || task.status}
                  </span>
                  {(task.status === 'queued' || task.status === 'running') && (
                    <button className={styles.cancelBtn} onClick={() => handleCancel(task.id)}>
                      <X size={12} />
                    </button>
                  )}
                </div>
              </div>
            ))}
            {tasks.length === 0 && <div className={styles.empty}>Нет задач</div>}
          </div>
        </div>
      </div>
    </div>
  )
}
