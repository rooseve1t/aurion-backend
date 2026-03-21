import { useEffect, useState } from 'react'
import { BrainCircuit, Sparkles } from 'lucide-react'
import { twinService } from '@/services/twin'
import { useToast } from '@/hooks/useToast'
import { formatDate } from '@/utils'
import type { TwinPrediction, TwinProfile } from '@/types'
import styles from './Workspace.module.css'

export function TwinPage() {
  const [profile, setProfile] = useState<TwinProfile | null>(null)
  const [predictions, setPredictions] = useState<TwinPrediction[]>([])
  const toast = useToast()

  useEffect(() => {
    Promise.all([twinService.getProfile(), twinService.getPredictions()])
      .then(([nextProfile, nextPredictions]) => {
        setProfile(nextProfile)
        setPredictions(nextPredictions)
      })
      .catch(() => toast.error('Не удалось собрать цифровой двойник'))
  }, [])

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.titleBlock}>
          <BrainCircuit size={20} color="var(--cyan)" />
          <div>
            <div className={styles.title}>DIGITAL TWIN</div>
            <div className={styles.subtitle}>Профиль поведения, зоны силы и предсказания ближайших сценариев</div>
          </div>
        </div>
        <div className={styles.badge}>focus {profile?.focus_index ?? 0}</div>
      </div>

      <div className={styles.grid}>
        <div className={styles.card}>
          <div className={styles.sectionTitle}>Архетип</div>
          <div className={styles.metricValue}>{profile?.archetype ?? '—'}</div>
          <div className={styles.metricLabel}>Голосовой профиль: {profile?.voice_persona ?? '—'}</div>
        </div>
        <div className={styles.card}>
          <div className={styles.sectionTitle}>Сильные стороны</div>
          <div className={styles.list}>
            {profile?.strengths.map((item) => (
              <div key={item} className={styles.itemMeta}>{item}</div>
            ))}
          </div>
        </div>
      </div>

      <div className={styles.grid}>
        <section className={styles.card}>
          <div className={styles.sectionTitle}>Рутины</div>
          <div className={styles.list}>
            {profile?.routines.map((item) => (
              <div key={item} className={styles.item}>{item}</div>
            ))}
          </div>
        </section>

        <section className={styles.card}>
          <div className={styles.sectionTitle}>Зоны внимания</div>
          <div className={styles.list}>
            {profile?.watchouts.map((item) => (
              <div key={item} className={styles.item}>{item}</div>
            ))}
          </div>
        </section>
      </div>

      <section className={styles.card}>
        <div className={styles.sectionTitle}>Предсказания</div>
        <div className={styles.list}>
          {predictions.map((item) => (
            <div key={item.id} className={styles.item}>
              <div className={styles.itemRow}>
                <div className={styles.itemTitle}>{item.title}</div>
                <div className={styles.badge}>{Math.round(item.confidence * 100)}%</div>
              </div>
              <div className={styles.itemMeta}>{item.message}</div>
              <div className={styles.badgeRow}>
                <span className={styles.badge}>{item.source}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.card}>
        <div className={styles.sectionTitle}>Опорные воспоминания</div>
        <div className={styles.list}>
          {profile?.memory_highlights.map((memory) => (
            <div key={memory.id} className={styles.item}>
              <div className={styles.itemTitle}>{memory.content}</div>
              <div className={styles.itemMeta}>
                Важность {memory.importance}/10 • {formatDate(memory.created_at)}
              </div>
              <div className={styles.badgeRow}>
                {memory.tags.map((tag) => <span key={tag} className={styles.badge}>{tag}</span>)}
              </div>
            </div>
          ))}
          {!profile?.memory_highlights.length && <div className={styles.empty}>Пока недостаточно сигналов</div>}
        </div>
      </section>

      <div className={styles.card}>
        <div className={styles.sectionTitle}>Статус</div>
        <div className={styles.itemMeta}>
          <Sparkles size={14} color="var(--cyan)" style={{ verticalAlign: 'middle', marginRight: 6 }} />
          Цифровой двойник строится на памяти, финансах, сценариях дома и активности агентов.
        </div>
      </div>
    </div>
  )
}
