import { useEffect, useState } from 'react'
import { BellRing, Check, Trash2 } from 'lucide-react'
import { remindersService } from '@/services/reminders'
import { useToast } from '@/hooks/useToast'
import { formatDate } from '@/utils'
import type { Reminder } from '@/types'
import styles from './Workspace.module.css'

const initialForm = {
  title: '',
  note: '',
  due_at: '',
  priority: 'medium' as Reminder['priority'],
}

export function RemindersPage() {
  const [items, setItems] = useState<Reminder[]>([])
  const [form, setForm] = useState(initialForm)
  const toast = useToast()

  const load = async () => {
    try {
      setItems(await remindersService.list())
    } catch {
      toast.error('Не удалось загрузить напоминания')
    }
  }

  useEffect(() => {
    load()
  }, [])

  const create = async (event: React.FormEvent) => {
    event.preventDefault()
    try {
      const reminder = await remindersService.create({
        title: form.title,
        note: form.note,
        due_at: form.due_at ? new Date(form.due_at).toISOString() : null,
        priority: form.priority,
      })
      setItems((current) => [reminder, ...current])
      setForm(initialForm)
      toast.success('Напоминание сохранено')
    } catch {
      toast.error('Не удалось создать напоминание')
    }
  }

  const updateStatus = async (item: Reminder, status: Reminder['status']) => {
    try {
      const updated = await remindersService.update(item.id, { status })
      setItems((current) => current.map((entry) => entry.id === item.id ? updated : entry))
    } catch {
      toast.error('Не удалось обновить напоминание')
    }
  }

  const remove = async (id: number) => {
    try {
      await remindersService.remove(id)
      setItems((current) => current.filter((entry) => entry.id !== id))
    } catch {
      toast.error('Не удалось удалить напоминание')
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.titleBlock}>
          <BellRing size={20} color="var(--cyan)" />
          <div>
            <div className={styles.title}>REMINDERS</div>
            <div className={styles.subtitle}>Личный слой напоминаний для системы, бизнеса и бытовых сценариев</div>
          </div>
        </div>
        <div className={styles.badge}>{items.filter((item) => item.status === 'pending').length} pending</div>
      </div>

      <form className={styles.card} onSubmit={create}>
        <div className={styles.sectionTitle}>Новое напоминание</div>
        <div className={styles.formGrid}>
          <input
            className="input"
            value={form.title}
            onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
            placeholder="Что нужно не забыть?"
            required
          />
          <input
            className="input"
            type="datetime-local"
            value={form.due_at}
            onChange={(event) => setForm((current) => ({ ...current, due_at: event.target.value }))}
          />
          <select
            className="input"
            value={form.priority}
            onChange={(event) => setForm((current) => ({ ...current, priority: event.target.value as Reminder['priority'] }))}
          >
            <option value="low">Низкий приоритет</option>
            <option value="medium">Средний приоритет</option>
            <option value="high">Высокий приоритет</option>
          </select>
        </div>
        <textarea
          className={styles.textArea}
          value={form.note}
          onChange={(event) => setForm((current) => ({ ...current, note: event.target.value }))}
          placeholder="Контекст, ссылка, важные детали..."
        />
        <div className={styles.actions}>
          <button type="submit" className="btn btn-cyan">СОХРАНИТЬ</button>
        </div>
      </form>

      <section className={styles.card}>
        <div className={styles.sectionTitle}>Список</div>
        <div className={styles.list}>
          {items.map((item) => (
            <div key={item.id} className={styles.item}>
              <div className={styles.itemRow}>
                <div className={styles.itemTitle}>{item.title}</div>
                <div className={styles.badge}>{item.status}</div>
              </div>
              {item.note && <div className={styles.itemMeta}>{item.note}</div>}
              <div className={styles.itemMeta}>
                {item.due_at ? formatDate(item.due_at) : 'Без дедлайна'}
              </div>
              <div className={styles.badgeRow}>
                <span className={`${styles.badge} ${
                  item.priority === 'high' ? styles.priorityHigh :
                  item.priority === 'low' ? styles.priorityLow :
                  styles.priorityMedium
                }`}>
                  {item.priority}
                </span>
              </div>
              <div className={styles.actions}>
                {item.status !== 'completed' && (
                  <button className="btn btn-ghost" onClick={() => updateStatus(item, 'completed')}>
                    <Check size={14} />
                    ЗАВЕРШИТЬ
                  </button>
                )}
                {item.status === 'completed' && (
                  <button className="btn btn-ghost" onClick={() => updateStatus(item, 'pending')}>
                    ВЕРНУТЬ В РАБОТУ
                  </button>
                )}
                <button className="btn btn-danger" onClick={() => remove(item.id)}>
                  <Trash2 size={14} />
                  УДАЛИТЬ
                </button>
              </div>
            </div>
          ))}
          {items.length === 0 && <div className={styles.empty}>Напоминаний пока нет</div>}
        </div>
      </section>
    </div>
  )
}
