import { useEffect } from 'react'
import { Cpu, Brain, Shield, Zap } from 'lucide-react'
import { useUiStore } from '@/store/uiStore'
import { systemService } from '@/services/system'

export function StatBar() {
  const { stats, setStats, setStatsLoading } = useUiStore()

  useEffect(() => {
    const load = async () => {
      setStatsLoading(true)
      try {
        const s = await systemService.getStats()
        setStats(s)
      } catch {
        // Fallback stats
        setStats({
          devices_online: 0, memory_entries: 0,
          active_tasks: 0, quantum_status: 'offline',
          subscription_tier: 'Free', uptime_hours: 0,
        })
      } finally {
        setStatsLoading(false)
      }
    }
    load()
    const interval = setInterval(load, 60000)
    return () => clearInterval(interval)
  }, [])

  const items = [
    { icon: Cpu,    label: 'КВАНТЫ',   value: stats?.quantum_status === 'online' ? 'ONLINE' : 'OFFLINE', color: stats?.quantum_status === 'online' ? 'text-cyan' : 'text-white/30' },
    { icon: Brain,  label: 'ПАМЯТЬ',   value: stats ? `${stats.memory_entries}` : '—',   color: 'text-purple' },
    { icon: Shield, label: 'ЗАДАЧИ',   value: stats ? `${stats.active_tasks}`    : '—',   color: 'text-emerald' },
    { icon: Zap,    label: 'ТАРИФ',    value: stats?.subscription_tier ?? 'Free',          color: 'text-amber' },
  ]

  return (
    <div className="flex gap-3 px-4 py-2 border-b border-cyan/10 bg-card/30 overflow-x-auto">
      {items.map((item) => {
        const Icon = item.icon
        return (
          <div key={item.label} className="flex items-center gap-2 min-w-fit">
            <Icon size={12} className={item.color} />
            <span className="text-[10px] text-white/30 tracking-wider">{item.label}</span>
            <span className={`text-[10px] font-bold tracking-wider ${item.color}`}>{item.value}</span>
          </div>
        )
      })}
    </div>
  )
}
