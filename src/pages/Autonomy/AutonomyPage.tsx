import { useState, useEffect } from 'react'
import { Cpu, Play, X, Brain, Database, Settings, LogOut, UserCheck, Lock, Terminal, LayoutDashboard, BarChart3, Zap } from 'lucide-react'
import { agentsService } from '@/services/agents'
import { useToast } from '@/hooks/useToast'
import type { Agent, AgentTask } from '@/types'
import { agentTypeLabel, taskStatusLabel, formatDate } from '@/utils'
import '@/styles/aurion-design-system.css'

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

  return (
    <div className="min-h-screen bg-[var(--aurion-bg-primary)] text-[var(--aurion-text-secondary)] font-body overflow-hidden">
      {/* TopAppBar */}
      <header className="fixed top-0 w-full z-50 flex justify-between items-center px-8 h-16 bg-[var(--aurion-bg-surface)]/60 backdrop-blur-xl border-b border-[var(--aurion-text-dim)]/15 shadow-[0_4px_20px_rgba(0,229,255,0.08)]">
        <div className="flex items-center gap-3">
          <div className="relative w-8 h-8 flex items-center justify-center">
            <div className="absolute inset-0 border border-[var(--aurion-cyan)]/40 rounded-full animate-spin" style={{ animationDuration: '3s' }}></div>
            <div className="absolute inset-1 border border-[var(--aurion-cyan)]/20 rounded-full animate-spin direction-reverse" style={{ animationDuration: '5s' }}></div>
            <div className="w-1.5 h-1.5 bg-[var(--aurion-cyan)] rounded-full shadow-[0_0_8px_var(--aurion-cyan)]"></div>
          </div>
          <span className="text-2xl font-black tracking-tighter text-[var(--aurion-cyan)] drop-shadow-[0_0_8px_rgba(0,229,255,0.4)]">AURION OS</span>
        </div>
        <nav className="hidden md:flex gap-8 h-full items-center">
          <a className="h-full flex items-center px-2 font-['Inter'] tracking-tight text-sm font-light uppercase text-[var(--aurion-text-muted)] hover:text-[var(--aurion-cyan)] hover:bg-[var(--aurion-bg-surface)] transition-all duration-300" href="#">СИСТЕМА</a>
          <a className="h-full flex items-center px-2 font-['Inter'] tracking-tight text-sm font-light uppercase text-[var(--aurion-cyan)] border-b-2 border-[var(--aurion-cyan)]" href="#">АВТОНОМИЯ</a>
          <a className="h-full flex items-center px-2 font-['Inter'] tracking-tight text-sm font-light uppercase text-[var(--aurion-text-muted)] hover:text-[var(--aurion-cyan)] hover:bg-[var(--aurion-bg-surface)] transition-all duration-300" href="#">ПРОТОКОЛЫ</a>
        </nav>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-4 text-[var(--aurion-cyan)]">
            <Settings size={20} />
            <Zap size={20} />
            <Cpu size={20} />
          </div>
        </div>
      </header>

      {/* SideNavBar */}
      <aside className="fixed left-0 top-16 h-[calc(100vh-64px)] w-64 flex flex-col py-6 bg-[var(--aurion-bg-primary)] border-r border-[var(--aurion-text-dim)]/15 z-40">
        <div className="px-6 mb-8">
          <div className="flex items-center gap-3 p-3 aurion-card rounded-xl">
            <div className="w-10 h-10 rounded-lg bg-[var(--aurion-cyan)]/10 flex items-center justify-center border border-[var(--aurion-cyan)]/20">
              <Terminal className="text-[var(--aurion-cyan)]" size={20} />
            </div>
            <div>
              <div className="font-['Inter'] text-[11px] font-medium tracking-widest uppercase text-[var(--aurion-text-secondary)]">Терминал</div>
              <div className="text-[10px] text-[var(--aurion-text-muted)] uppercase tracking-tighter">Автономия</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-1">
          <a className="flex items-center gap-4 px-6 py-3 text-[var(--aurion-text-muted)] hover:bg-[var(--aurion-bg-surface-low)] hover:text-[var(--aurion-cyan)] transition-colors duration-300 group" href="#">
            <LayoutDashboard size={16} />
            <span className="font-['Inter'] text-[11px] font-medium tracking-widest uppercase">Обзор</span>
          </a>
          <a className="flex items-center gap-4 px-6 py-3 text-[var(--aurion-cyan)] font-bold bg-[var(--aurion-bg-surface)] border-l-4 border-[var(--aurion-cyan)] transition-all duration-200" href="#">
            <Cpu size={16} />
            <span className="font-['Inter'] text-[11px] font-medium tracking-widest uppercase">Агенты</span>
          </a>
          <a className="flex items-center gap-4 px-6 py-3 text-[var(--aurion-text-muted)] hover:bg-[var(--aurion-bg-surface-low)] hover:text-[var(--aurion-cyan)] transition-colors duration-300 group" href="#">
            <Play size={16} />
            <span className="font-['Inter'] text-[11px] font-medium tracking-widest uppercase">Задачи</span>
          </a>
          <a className="flex items-center gap-4 px-6 py-3 text-[var(--aurion-text-muted)] hover:bg-[var(--aurion-bg-surface-low)] hover:text-[var(--aurion-cyan)] transition-colors duration-300 group" href="#">
            <BarChart3 size={16} />
            <span className="font-['Inter'] text-[11px] font-medium tracking-widest uppercase">Метрики</span>
          </a>
          <a className="flex items-center gap-4 px-6 py-3 text-[var(--aurion-text-muted)] hover:bg-[var(--aurion-bg-surface-low)] hover:text-[var(--aurion-cyan)] transition-colors duration-300 group" href="#">
            <Zap size={16} />
            <span className="font-['Inter'] text-[11px] font-medium tracking-widest uppercase">Ядро</span>
          </a>
        </nav>
        <div className="px-6 mt-auto">
          <button className="w-full py-3 aurion-btn aurion-btn-primary font-bold text-[10px] tracking-widest uppercase rounded-lg">
            Создать Агента
          </button>
          <div className="mt-6 border-t border-[var(--aurion-text-dim)]/10 pt-6 space-y-4">
            <a className="flex items-center gap-4 text-[var(--aurion-text-muted)] hover:text-[var(--aurion-cyan)] transition-colors duration-300" href="#">
              <Settings size={14} />
              <span className="font-['Inter'] text-[10px] font-medium tracking-widest uppercase">Настройки</span>
            </a>
            <a className="flex items-center gap-4 text-[var(--aurion-text-muted)] hover:text-[var(--aurion-error)] transition-colors duration-300" href="#">
              <LogOut size={14} />
              <span className="font-['Inter'] text-[10px] font-medium tracking-widest uppercase">Выход</span>
            </a>
          </div>
        </div>
      </aside>

      {/* Main Canvas */}
      <main className="ml-64 pt-20 p-8 h-screen overflow-hidden flex flex-col">
        {/* Dashboard Header */}
        <div className="flex justify-between items-end mb-10">
          <div>
            <span className="aurion-label text-[var(--aurion-text-muted)] font-medium tracking-[0.2em] uppercase text-[10px]">Управление Агентами</span>
            <h1 className="text-4xl font-black tracking-tighter mt-1 text-[var(--aurion-text-secondary)]">ЦЕНТР УПРАВЛЕНИЯ</h1>
          </div>
          <div className="flex gap-4">
            <div className="px-4 py-2 aurion-card rounded-lg flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-[var(--aurion-cyan)] aurion-pulse"></div>
              <span className="text-[11px] font-bold tracking-widest uppercase">Система Стабильна</span>
            </div>
          </div>
        </div>

        {/* Grid Layout */}
        <div className="flex-1 grid grid-cols-12 gap-6 overflow-hidden min-h-0">
          {/* Left Column: Active Agents */}
          <section className="col-span-3 flex flex-col gap-4 overflow-y-auto pr-2 aurion-scrollbar">
            <h3 className="aurion-label text-[var(--aurion-text-muted)]/60 font-medium tracking-[0.1em] uppercase text-[9px] mb-2 px-2">Активные Агенты ({agents.length})</h3>
            
            {agents.length === 0 && !loading && (
              <div className="aurion-card p-8 text-center">
                <Brain className="text-[var(--aurion-text-muted)] mx-auto mb-4" size={32} />
                <p className="text-[var(--aurion-text-muted)]">Нет агентов</p>
              </div>
            )}
            
            {agents.map((agent) => (
              <div key={agent.id} className="aurion-card p-4 hover:bg-[var(--aurion-bg-surface-high)] transition-all group cursor-pointer">
                <div className="flex justify-between items-start mb-4">
                  <div className="w-8 h-8 rounded-lg bg-[var(--aurion-cyan)]/10 border border-[var(--aurion-cyan)]/30 flex items-center justify-center">
                    <Brain className="text-[var(--aurion-cyan)]" size={16} />
                  </div>
                  <span className="text-[9px] font-bold bg-[var(--aurion-cyan)]/20 text-[var(--aurion-cyan)] px-2 py-1 rounded">ACTIVE</span>
                </div>
                <h4 className="font-bold text-sm mb-1 tracking-tight">{agent.name}</h4>
                <p className="text-[10px] text-[var(--aurion-text-muted)] uppercase tracking-widest">ID: {agent.id}</p>
                <p className="text-[10px] text-[var(--aurion-text-muted)] uppercase tracking-widest">{agentTypeLabel[agent.agent_type] || agent.agent_type}</p>
                <div className="mt-4 pt-4 border-t border-[var(--aurion-text-dim)]/10 flex justify-between items-center">
                  <span className="text-[9px] text-[var(--aurion-text-muted)]">Нагрузка: 42%</span>
                  <div className="w-16 h-1 bg-[var(--aurion-bg-surface-lowest)] rounded-full overflow-hidden">
                    <div className="h-full bg-[var(--aurion-cyan)] w-[42%]"></div>
                  </div>
                </div>
                <button 
                  className="aurion-btn aurion-btn-primary w-full mt-3 py-2 text-xs"
                  onClick={() => handleRunTask(agent)}
                >
                  <Play size={10} />
                  ЗАПУСК
                </button>
              </div>
            ))}
          </section>

          {/* Middle Column: Task Queue */}
          <section className="col-span-6 flex flex-col gap-6 aurion-card p-6 overflow-hidden">
            <div className="flex justify-between items-center">
              <h3 className="aurion-label text-[var(--aurion-cyan)] font-bold tracking-[0.2em] uppercase text-[11px]">Журнал Задач</h3>
              <div className="flex gap-2">
                <span className="w-2 h-2 rounded-full bg-[var(--aurion-cyan)]/40"></span>
                <span className="w-2 h-2 rounded-full bg-[var(--aurion-cyan)]/20"></span>
                <span className="w-2 h-2 rounded-full bg-[var(--aurion-cyan)]/10"></span>
              </div>
            </div>
            
            <div className="flex-1 overflow-y-auto space-y-4 pr-2 aurion-scrollbar font-mono text-[11px]">
              {tasks.length === 0 && (
                <div className="aurion-card p-8 text-center">
                  <Play className="text-[var(--aurion-text-muted)] mx-auto mb-4" size={32} />
                  <p className="text-[var(--aurion-text-muted)]">Нет задач</p>
                </div>
              )}
              
              {tasks.map((task) => (
                <div key={task.id} className="aurion-card p-4 rounded-lg border-l-2 border-[var(--aurion-cyan)]/60 group">
                  <div className="flex justify-between mb-2">
                    <span className="text-[var(--aurion-cyan)]">[PROC_{task.id.toString().padStart(4, '0')}]</span>
                    <span className="text-[var(--aurion-text-muted)]">{formatDate(task.created_at)}</span>
                  </div>
                  <p className="text-[var(--aurion-text-secondary)] mb-3 uppercase tracking-tight">{task.action}</p>
                  {task.status === 'running' && (
                    <div className="w-full h-1 bg-[var(--aurion-bg-surface-high)] rounded-full overflow-hidden">
                      <div className="h-full bg-[var(--aurion-cyan)] w-[75%] transition-all duration-1000"></div>
                    </div>
                  )}
                  <div className="mt-2 flex justify-between items-center text-[9px] text-[var(--aurion-text-muted)]/60">
                    <span>Status: {taskStatusLabel[task.status] || task.status}</span>
                    <span style={{ color: STATUS_COLOR[task.status] || 'var(--aurion-text-muted)' }}>
                      {task.status === 'completed' && '✓'}
                      {task.status === 'running' && '⏳'}
                      {task.status === 'failed' && '✗'}
                      {task.status === 'queued' && '⏸'}
                    </span>
                  </div>
                  {(task.status === 'queued' || task.status === 'running') && (
                    <button 
                      className="mt-2 text-[var(--aurion-error)] hover:text-[var(--aurion-error)]/80 transition-colors"
                      onClick={() => handleCancel(task.id)}
                    >
                      <X size={12} />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </section>

          {/* Right Column: Performance Metrics */}
          <section className="col-span-3 flex flex-col gap-6">
            {/* Metric 1: Core Load */}
            <div className="aurion-card p-6 relative overflow-hidden">
              <div className="relative z-10">
                <h4 className="aurion-label text-[var(--aurion-text-muted)] uppercase tracking-widest text-[10px] mb-1">Загрузка Ядра</h4>
                <div className="text-3xl font-black text-[var(--aurion-cyan)]">68.4%</div>
                <div className="mt-4 flex items-end gap-1 h-12">
                  <div className="w-full bg-[var(--aurion-cyan)]/20 h-[30%] rounded-sm"></div>
                  <div className="w-full bg-[var(--aurion-cyan)]/40 h-[45%] rounded-sm"></div>
                  <div className="w-full bg-[var(--aurion-cyan)]/60 h-[80%] rounded-sm"></div>
                  <div className="w-full bg-[var(--aurion-cyan)]/30 h-[20%] rounded-sm"></div>
                  <div className="w-full bg-[var(--aurion-cyan)]/70 h-[90%] rounded-sm"></div>
                  <div className="w-full bg-[var(--aurion-cyan)] h-[68%] rounded-sm"></div>
                </div>
              </div>
              <div className="absolute -right-4 -bottom-4 opacity-5 pointer-events-none">
                <Cpu size={64} />
              </div>
            </div>

            {/* Metric 2: Synapse Activity */}
            <div className="aurion-card p-6">
              <h4 className="aurion-label text-[var(--aurion-text-muted)] uppercase tracking-widest text-[10px] mb-1">Активность Синапсов</h4>
              <div className="text-3xl font-black text-[var(--aurion-text-secondary)]">1.2 TB/s</div>
              <div className="mt-6 flex flex-col gap-3">
                <div className="flex justify-between items-center text-[10px]">
                  <span className="text-[var(--aurion-text-muted)]">Входящие</span>
                  <span className="text-[var(--aurion-cyan)] font-bold">842 GB/s</span>
                </div>
                <div className="w-full h-1 bg-[var(--aurion-bg-surface-lowest)] rounded-full overflow-hidden">
                  <div className="h-full bg-[var(--aurion-cyan)] w-[70%]"></div>
                </div>
                <div className="flex justify-between items-center text-[10px]">
                  <span className="text-[var(--aurion-text-muted)]">Исходящие</span>
                  <span className="text-[var(--aurion-text-secondary)] font-bold">358 GB/s</span>
                </div>
                <div className="w-full h-1 bg-[var(--aurion-bg-surface-lowest)] rounded-full overflow-hidden">
                  <div className="h-full bg-[var(--aurion-text-secondary)]/40 w-[30%]"></div>
                </div>
              </div>
            </div>

            {/* Metric 3: Autonomy Level */}
            <div className="aurion-card p-6 flex-1 flex flex-col justify-center items-center relative">
              <h4 className="aurion-label text-[var(--aurion-text-muted)] uppercase tracking-widest text-[10px] mb-4">Уровень Автономии</h4>
              <div className="relative w-32 h-32 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle className="text-[var(--aurion-text-dim)]/20" cx="64" cy="64" fill="transparent" r="58" stroke="currentColor" strokeWidth="2"></circle>
                  <circle className="text-[var(--aurion-cyan)] drop-shadow-[0_0_8px_var(--aurion-cyan)]" cx="64" cy="64" fill="transparent" r="58" stroke="currentColor" strokeDasharray="364.4" strokeDashoffset="36.4" strokeWidth="4"></circle>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-2xl font-black">90%</span>
                  <span className="text-[8px] uppercase tracking-tighter text-[var(--aurion-cyan)]">Sovereign</span>
                </div>
              </div>
              <p className="text-[9px] text-center mt-4 text-[var(--aurion-text-muted)]/60 uppercase leading-relaxed tracking-widest">
                Система принимает 9 из 10 решений самостоятельно.
              </p>
            </div>
          </section>
        </div>

        {/* Bottom Footer */}
        <footer className="h-12 border-t border-[var(--aurion-text-dim)]/10 flex justify-between items-center px-2 mt-6">
          <div className="flex gap-8 text-[10px] tracking-widest font-medium uppercase text-[var(--aurion-text-muted)]/60">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--aurion-cyan)]/40"></span>
              <span>Uptime: 142d 18h 04m</span>
            </div>
            <div className="flex items-center gap-2">
              <Lock size={12} />
              <span>Encryption: Quantum AES-512</span>
            </div>
            <div className="flex items-center gap-2">
              <Database size={12} />
              <span>DB Sync: Localized</span>
            </div>
          </div>
          <div className="flex items-center gap-2 text-[10px] text-[var(--aurion-cyan)]/80 font-bold uppercase tracking-widest">
            <UserCheck size={14} />
            <span>SECURE TERMINAL</span>
          </div>
        </footer>
      </main>

      {/* Contextual HUD Element (Floating) */}
      <div className="fixed right-10 top-24 pointer-events-none opacity-20 hidden xl:block">
        <div className="text-[8px] font-mono space-y-1">
          <div className="flex justify-between gap-10"><span>LATENCY</span><span>0.002ms</span></div>
          <div className="flex justify-between gap-10"><span>COORD_X</span><span>45.022.1</span></div>
          <div className="flex justify-between gap-10"><span>COORD_Y</span><span>10.884.9</span></div>
          <div className="flex justify-between gap-10"><span>VECTOR</span><span>RISING</span></div>
          <div className="w-full h-[1px] bg-[var(--aurion-cyan)]/40 my-2"></div>
          <div className="flex justify-between gap-10"><span>AUTH</span><span>AUTHORIZED</span></div>
        </div>
      </div>
    </div>
  )
}
