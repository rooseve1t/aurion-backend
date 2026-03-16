import { useState, useEffect, useCallback } from 'react'
import { Search, Trash2, Plus, Brain } from 'lucide-react'
import { memoryService } from '@/services/memory'
import type { MemoryEntry } from '@/types'
import { formatDate, truncate } from '@/utils'
import toast from 'react-hot-toast'

export default function MemoryPage() {
  const [entries, setEntries] = useState<MemoryEntry[]>([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [addMode, setAddMode] = useState(false)
  const [newContent, setNewContent] = useState('')
  const [newImportance, setNewImportance] = useState(0.5)

  const search = useCallback(async (q: string) => {
    setLoading(true)
    try {
      const results = await memoryService.search(q || '', 30, q ? 0.3 : 0.0)
      setEntries(results)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => search(query), 300)
    return () => clearTimeout(timer)
  }, [query, search])

  const handleDelete = async (id: number) => {
    await memoryService.delete(id)
    setEntries((e) => e.filter((m) => m.id !== id))
    toast.success('Запись удалена')
  }

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newContent.trim()) return
    try {
      const entry = await memoryService.add(newContent, newImportance)
      setEntries((prev) => [entry, ...prev])
      setNewContent('')
      setAddMode(false)
      toast.success('Запись добавлена')
    } catch {
      toast.error('Ошибка добавления')
    }
  }

  const importanceColor = (v: number) =>
    v >= 0.8 ? 'text-danger' : v >= 0.5 ? 'text-amber' : 'text-emerald'

  return (
    <div className="p-4 max-w-3xl mx-auto space-y-4" data-testid="memory-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain size={20} className="text-purple" />
          <div>
            <div className="font-bold text-sm tracking-wider">ВЕКТОРНАЯ ПАМЯТЬ</div>
            <div className="text-[10px] text-white/30">{entries.length} записей</div>
          </div>
        </div>
        <button
          onClick={() => setAddMode(!addMode)}
          className="flex items-center gap-2 px-3 py-1.5 bg-purple/10 hover:bg-purple/20 border border-purple/30 text-purple text-xs rounded transition-all"
        >
          <Plus size={14} /> Добавить
        </button>
      </div>

      {/* Add form */}
      {addMode && (
        <form onSubmit={handleAdd} className="bg-card border border-purple/20 rounded-lg p-4 space-y-3 animate-fade-in">
          <textarea
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="Содержимое записи..."
            rows={3}
            className="w-full bg-surface border border-white/10 rounded px-3 py-2 text-sm text-white placeholder-white/30 focus:outline-none focus:border-purple/40 resize-none"
          />
          <div className="flex items-center gap-3">
            <label className="text-xs text-white/40">Важность: {newImportance.toFixed(1)}</label>
            <input type="range" min={0} max={1} step={0.1} value={newImportance}
              onChange={(e) => setNewImportance(Number(e.target.value))}
              className="flex-1 accent-purple" />
          </div>
          <div className="flex gap-2">
            <button type="submit" className="px-4 py-1.5 bg-purple/20 border border-purple/40 text-purple text-xs rounded">Сохранить</button>
            <button type="button" onClick={() => setAddMode(false)} className="px-4 py-1.5 text-white/30 text-xs">Отмена</button>
          </div>
        </form>
      )}

      {/* Search */}
      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Поиск по памяти..."
          className="w-full bg-card border border-white/10 rounded pl-9 pr-4 py-2.5 text-sm text-white placeholder-white/30 focus:outline-none focus:border-cyan/40"
        />
      </div>

      {/* Entries */}
      {loading ? (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-card border border-white/5 rounded animate-pulse" />
          ))}
        </div>
      ) : entries.length === 0 ? (
        <div className="text-center py-16 text-white/20 text-sm">
          {query ? 'По запросу ничего не найдено' : 'Память пуста'}
        </div>
      ) : (
        <div className="space-y-2" data-testid="memory-list">
          {entries.map((entry) => (
            <div
              key={entry.id}
              className="bg-card border border-white/8 rounded-lg p-3 flex gap-3 group hover:border-purple/20 transition-all animate-fade-in"
            >
              <div className="flex-1 min-w-0 space-y-1">
                <div className="text-sm text-white/80 leading-relaxed">{truncate(entry.content, 150)}</div>
                <div className="flex gap-3 text-[10px] text-white/30">
                  <span className="text-teal">{entry.source}</span>
                  <span>{formatDate(entry.created_at)}</span>
                  {entry.similarity !== undefined && (
                    <span className="text-purple">~{(entry.similarity * 100).toFixed(0)}%</span>
                  )}
                </div>
              </div>
              <div className="flex flex-col items-end gap-2 flex-shrink-0">
                <span className={`text-[10px] font-bold ${importanceColor(entry.importance)}`}>
                  {entry.importance.toFixed(1)}
                </span>
                <button
                  onClick={() => handleDelete(entry.id)}
                  className="opacity-0 group-hover:opacity-100 text-white/20 hover:text-danger transition-all"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
