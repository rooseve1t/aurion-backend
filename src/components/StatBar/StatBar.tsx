import styles from './StatBar.module.css'
import type { SystemStats } from '@/types'

interface Props { stats: SystemStats | null }

const items = (s: SystemStats) => [
  { label: 'УСТРОЙСТВА', value: s.devices_online, color: 'var(--cyan)', unit: '' },
  { label: 'ПАМЯТЬ',     value: s.memory_entries, color: 'var(--teal)', unit: '' },
  { label: 'ЗАДАЧИ',     value: s.active_tasks,   color: 'var(--purple)', unit: '' },
  {
    label: 'КВАНТУМ',
    value: s.quantum_status === 'online' ? '●' : '○',
    color: s.quantum_status === 'online' ? 'var(--green)' : 'var(--text-muted)',
    unit: '',
  },
]

export function StatBar({ stats }: Props) {
  if (!stats) {
    return (
      <div className={styles.bar}>
        {['УСТРОЙСТВА','ПАМЯТЬ','ЗАДАЧИ','КВАНТУМ'].map((l) => (
          <div key={l} className={styles.item}>
            <span className={styles.label}>{l}</span>
            <span className={styles.value} style={{ color: 'var(--border)' }}>—</span>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className={styles.bar}>
      {items(stats).map(({ label, value, color, unit }) => (
        <div key={label} className={styles.item}>
          <span className={styles.label}>{label}</span>
          <span className={styles.value} style={{ color }}>
            {value}{unit}
          </span>
        </div>
      ))}
    </div>
  )
}
