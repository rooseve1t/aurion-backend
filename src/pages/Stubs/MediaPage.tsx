import { useEffect, useState } from 'react'
import { Headphones, Play, Pause, CheckCircle2 } from 'lucide-react'
import { mediaService } from '@/services/media'
import { useToast } from '@/hooks/useToast'
import type { MediaItem } from '@/types'
import styles from './Workspace.module.css'

const initialForm = {
  title: '',
  media_type: 'playlist' as MediaItem['media_type'],
  mood: 'focus' as MediaItem['mood'],
  duration_minutes: 30,
  description: '',
}

export function MediaPage() {
  const [items, setItems] = useState<MediaItem[]>([])
  const [form, setForm] = useState(initialForm)
  const toast = useToast()

  const load = async () => {
    try {
      setItems(await mediaService.list())
    } catch {
      toast.error('Не удалось загрузить медиасценарии')
    }
  }

  useEffect(() => {
    load()
  }, [])

  const create = async (event: React.FormEvent) => {
    event.preventDefault()
    try {
      const item = await mediaService.create(form)
      setItems((current) => [item, ...current])
      setForm(initialForm)
      toast.success('Медиа-сценарий создан')
    } catch {
      toast.error('Не удалось создать медиасценарий')
    }
  }

  const updateStatus = async (item: MediaItem, status: MediaItem['status']) => {
    try {
      const updated = await mediaService.updateStatus(item.id, status)
      setItems((current) => current.map((entry) => entry.id === item.id ? updated : entry))
    } catch {
      toast.error('Не удалось обновить статус')
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.titleBlock}>
          <Headphones size={20} color="var(--cyan)" />
          <div>
            <div className={styles.title}>MEDIA SPACE</div>
            <div className={styles.subtitle}>Плейлисты, аудио-брифинги и атмосфера дома под нужный режим</div>
          </div>
        </div>
      </div>

      <form className={styles.card} onSubmit={create}>
        <div className={styles.sectionTitle}>Новый медиасценарий</div>
        <div className={styles.formGrid}>
          <input
            className="input"
            value={form.title}
            onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
            placeholder="Название"
            required
          />
          <select
            className="input"
            value={form.media_type}
            onChange={(event) => setForm((current) => ({ ...current, media_type: event.target.value as MediaItem['media_type'] }))}
          >
            <option value="playlist">Playlist</option>
            <option value="music">Music</option>
            <option value="briefing">Briefing</option>
            <option value="video">Video</option>
          </select>
          <select
            className="input"
            value={form.mood}
            onChange={(event) => setForm((current) => ({ ...current, mood: event.target.value as MediaItem['mood'] }))}
          >
            <option value="focus">Focus</option>
            <option value="calm">Calm</option>
            <option value="insight">Insight</option>
            <option value="warning">Warning</option>
          </select>
          <input
            className="input"
            type="number"
            min={1}
            max={600}
            value={form.duration_minutes}
            onChange={(event) => setForm((current) => ({ ...current, duration_minutes: Number(event.target.value) }))}
          />
        </div>
        <textarea
          className={styles.textArea}
          value={form.description}
          onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
          placeholder="Что должен делать этот медиасценарий?"
        />
        <button type="submit" className="btn btn-cyan">ДОБАВИТЬ</button>
      </form>

      <section className={styles.card}>
        <div className={styles.sectionTitle}>Библиотека</div>
        <div className={styles.list}>
          {items.map((item) => (
            <div key={item.id} className={styles.item}>
              <div className={styles.itemRow}>
                <div className={styles.itemTitle}>{item.title}</div>
                <div className={styles.badge}>{item.status}</div>
              </div>
              <div className={styles.itemMeta}>
                {item.media_type} • {item.duration_minutes} мин • {item.mood}
              </div>
              {item.description && <div className={styles.itemMeta}>{item.description}</div>}
              <div className={styles.actions}>
                {item.status !== 'active' && (
                  <button className="btn btn-cyan" onClick={() => updateStatus(item, 'active')}>
                    <Play size={14} />
                    АКТИВИРОВАТЬ
                  </button>
                )}
                {item.status === 'active' && (
                  <button className="btn btn-ghost" onClick={() => updateStatus(item, 'paused')}>
                    <Pause size={14} />
                    ПАУЗА
                  </button>
                )}
                {item.status !== 'completed' && (
                  <button className="btn btn-ghost" onClick={() => updateStatus(item, 'completed')}>
                    <CheckCircle2 size={14} />
                    ЗАВЕРШИТЬ
                  </button>
                )}
              </div>
            </div>
          ))}
          {items.length === 0 && <div className={styles.empty}>Пока нет медиасценариев</div>}
        </div>
      </section>
    </div>
  )
}
