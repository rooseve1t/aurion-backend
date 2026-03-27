import { useState, useEffect, useCallback } from 'react'
import { Search, Trash2, Plus, Brain } from 'lucide-react'
import { memoryService } from '@/services/memory'
import { useToast } from '@/hooks/useToast'
import type { MemoryEntry } from '@/types'
import { formatDate } from '@/utils'
import styles from './MemoryPage.module.css'

export function MemoryPage() {
  const [entries, setEntries]     = useState<MemoryEntry[]>([])
  const [query, setQuery]         = useState('')
  const [loading, setLoading]     = useState(false)
  const [adding, setAdding]       = useState(false)
  const [newContent, setNewContent] = useState('')
  const [importance, setImportance] = useState(5)
  const [count, setCount]         = useState(0)
  const toast = useToast()

  const search = useCallback(async (q: string) => {
    setLoading(true)
    try {
      const res = await memoryService.search(q, 50)
      setEntries(res)
    } catch { toast.error('Ошибка загрузки памяти') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => {
    search('')
    memoryService.count().then(setCount).catch(() => {})
  }, [search])

  useEffect(() => {
    const t = setTimeout(() => search(query), 400)
    return () => clearTimeout(t)
  }, [query, search])

  const handleDelete = async (id: number) => {
    try {
      await memoryService.delete(id)
      setEntries((e) => e.filter((x) => x.id !== id))
      setCount((c) => c - 1)
      toast.success('Запись удалена')
    } catch { toast.error('Ошибка удаления') }
  }

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newContent.trim()) return
    try {
      const entry = await memoryService.create(newContent.trim(), importance, [])
      setEntries((es) => [entry, ...es])
      setCount((c) => c + 1)
      setNewContent('')
      setAdding(false)
      toast.success('Запись добавлена')
    } catch { toast.error('Ошибка добавления') }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div className={styles.titleRow}>
          <Brain size={20} color="var(--cyan)" />
          <span className={styles.title}>ВЕКТОРНАЯ ПАМЯТЬ</span>
          <span className={styles.count}>{count} записей</span>
        </div>
        <div className={styles.statsStrip}>
          <div className={styles.statChip}><span>Всего</span><strong>{count}</strong></div>
          <div className={styles.statChip}><span>Важных</span><strong>{entries.filter((entry) => entry.importance >= 8).length}</strong></div>
          <div className={styles.statChip}><span>Последний доступ</span><strong>{entries[0] ? formatDate(entries[0].created_at) : '—'}</strong></div>
        </div>
        <div className={styles.actions}>
          <div className={styles.searchWrap}>
            <Search size={14} className={styles.searchIcon} />
            <input
              className={`input ${styles.searchInput}`}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Семантический поиск..."
            />
          </div>
          <button className="btn btn-cyan" onClick={() => setAdding(!adding)}>
            <Plus size={14} /> ДОБАВИТЬ
          </button>
        </div>
      </div>

      {adding && (
        <form className={styles.addForm} onSubmit={handleAdd}>
          <textarea
            className="input"
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="Содержимое записи..."
            rows={3}
            style={{ resize: 'vertical' }}
            autoFocus
          />
          <div className={styles.addRow}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <label className="label" style={{ margin: 0 }}>ВАЖНОСТЬ:</label>
              <input type="range" min={1} max={10} value={importance}
                onChange={(e) => setImportance(+e.target.value)} className={styles.range} />
              <span style={{ color: 'var(--cyan)', minWidth: 16 }}>{importance}</span>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button type="button" className="btn btn-ghost" onClick={() => setAdding(false)}>ОТМЕНА</button>
              <button type="submit" className="btn btn-cyan">СОХРАНИТЬ</button>
            </div>
          </div>
        </form>
      )}

      <div className={styles.list}>
        {loading && <div className={styles.loading}>ПОИСК...</div>}
        {!loading && entries.length === 0 && (
          <div className={styles.empty}>
            <Brain size={40} color="var(--border)" />
            <p>{query ? 'Ничего не найдено' : 'Нет записей в памяти'}</p>
          </div>
        )}
        {entries.map((entry) => (
          <MemoryCard key={entry.id} entry={entry} onDelete={handleDelete} />
        ))}
      </div>
    </div>
  )
}

function MemoryCard({ entry, onDelete }: { entry: MemoryEntry; onDelete: (id: number) => void }) {
  const impColor = entry.importance >= 8 ? 'var(--red)'
    : entry.importance >= 5 ? 'var(--amber)' : 'var(--text-muted)'
  return (
    <div className={styles.card} data-testid="memory-card">
      <div className={styles.cardTop}>
        <div className={styles.tags}>
          {entry.tags?.map((t) => (
            <span key={t} className={styles.tag}>{t}</span>
          ))}
        </div>
        <div className={styles.cardMeta}>
          <span className={styles.importance} style={{ color: impColor }}>
            ★ {entry.importance}/10
          </span>
          {entry.similarity !== undefined && (
            <span className={styles.similarity}>
              {Math.round(entry.similarity * 100)}%
            </span>
          )}
          <button className={styles.delBtn} onClick={() => onDelete(entry.id)}>
            <Trash2 size={12} />
          </button>
        </div>
      </div>
      <p className={styles.content}>{entry.content}</p>
      <span className={styles.date}>{formatDate(entry.created_at)}</span>
    </div>
  )
}
