import { useState, useEffect } from 'react'
import { Cpu, Play, X, Brain, Activity, Shield } from 'lucide-react'
import { agentsService } from '@/services/agents'
import { useToast } from '@/hooks/useToast'
import type { Agent, AgentTask } from '@/types'
import { agentTypeLabel, taskStatusLabel, formatDate } from '@/utils'
import styles from './AutonomyPage.module.css'

const STATUS_TONE: Record<string, string> = {
  queued: 'queued',
  running: 'running',
  completed: 'completed',
  failed: 'failed',
  cancelled: 'cancelled',
}

export function AutonomyPage() {
  const [agents, setAgents]   = useState<Agent[]>([])
  const [tasks, setTasks]     = useState<AgentTask[]>([])
  const [loading, setLoading] = useState(false)
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

  const handleRunTask = async (agent: Agent) => {
    try {
      const task = await agentsService.createTask(agent.id, 'default', {})
      setTasks((t) => [task, ...t])
      toast.success(`Задача создана для ${agent.name}`)
    } catch { toast.error('Ошибка запуска') }
  }

  const handleCancel = async (id: string) => {
    try {
      await agentsService.cancelTask(id)
      setTasks((t) => t.map((task) => task.id === id ? { ...task, status: 'cancelled' } : task))
    } catch { toast.error('Ошибка отмены') }
  }

  const runningTasks = tasks.filter((t) => t.status === 'running').length
  const completedTasks = tasks.filter((t) => t.status === 'completed').length
  const failedTasks = tasks.filter((t) => t.status === 'failed').length

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerTitle}>
          <Cpu size={20} color="var(--amber)" />
          <div>
            <div className={styles.kicker}>Autonomy Control</div>
            <h1 className={styles.title}>ЦЕНТР АВТОНОМНОСТИ</h1>
          </div>
        </div>
        <button className="btn btn-ghost" onClick={refresh} disabled={loading}>
          {loading ? 'ОБНОВЛЯЮ...' : 'ОБНОВИТЬ'}
        </button>
      </header>

      <section className={styles.summary}>
        <div className={styles.summaryCard}>
          <span>Активных агентов</span>
          <strong>{agents.length}</strong>
        </div>
        <div className={styles.summaryCard}>
          <span>Очередь задач</span>
          <strong>{tasks.length}</strong>
        </div>
        <div className={styles.summaryCard}>
          <span>Выполняется</span>
          <strong>{runningTasks}</strong>
        </div>
        <div className={styles.summaryCard}>
          <span>Ошибок</span>
          <strong>{failedTasks}</strong>
        </div>
      </section>

      <div className={styles.grid}>
        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <div className={styles.panelKicker}>Agents</div>
              <h2 className={styles.panelTitle}>Активные модули</h2>
            </div>
            <span className={styles.panelBadge}>{agents.length} ONLINE</span>
          </div>
          <div className={styles.panelBody}>
            {agents.length === 0 && !loading && (
              <div className={styles.empty}>
                <Brain size={32} />
                <span>Агенты не зарегистрированы</span>
              </div>
            )}
            {agents.map((agent) => (
              <div key={agent.id} className={styles.agentCard}>
                <div>
                  <div className={styles.agentName}>{agent.name}</div>
                  <div className={styles.agentMeta}>{agentTypeLabel[agent.agent_type] || agent.agent_type}</div>
                  <div className={styles.agentMeta}>ID: {agent.id}</div>
                </div>
                <button className="btn btn-cyan" onClick={() => handleRunTask(agent)}>
                  <Play size={14} /> Запуск
                </button>
              </div>
            ))}
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.panelHeader}>
            <div>
              <div className={styles.panelKicker}>Tasks</div>
              <h2 className={styles.panelTitle}>Журнал миссий</h2>
            </div>
            <span className={styles.panelBadge}>{completedTasks} OK</span>
          </div>
          <div className={styles.panelBody}>
            {tasks.length === 0 && !loading && (
              <div className={styles.empty}>
                <Activity size={32} />
                <span>Нет активных задач</span>
              </div>
            )}
            {tasks.map((task) => (
              <div key={task.id} className={styles.taskRow}>
                <div>
                  <div className={styles.taskTitle}>{task.action}</div>
                  <div className={styles.taskMeta}>{formatDate(task.created_at)}</div>
                </div>
                <div className={styles.taskRight}>
                  <span className={`${styles.status} ${styles[STATUS_TONE[task.status] || 'queued']}`}>
                    {taskStatusLabel[task.status] || task.status}
                  </span>
                  {(task.status === 'running' || task.status === 'queued') && (
                    <button className={styles.cancelBtn} onClick={() => handleCancel(task.id)}>
                      <X size={12} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <footer className={styles.footer}>
        <div className={styles.footerItem}>
          <Shield size={14} />
          Контур автономности стабилен
        </div>
      </footer>
    </div>
  )
}
