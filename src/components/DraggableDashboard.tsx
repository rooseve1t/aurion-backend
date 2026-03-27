/**
 * DraggableDashboard — настраиваемый дашборд с drag-and-drop виджетами.
 * Конфигурация сохраняется на сервере и восстанавливается при входе.
 */
import React, { useEffect, useState, useCallback } from 'react'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  rectSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { api } from '@/services/api'

// ─── Типы ─────────────────────────────────────────────────────────────────────

interface WidgetConfig {
  id: string
  type: string
  title: string
  order: number
  visible: boolean
}

// ─── Один виджет ──────────────────────────────────────────────────────────────

const SortableWidget: React.FC<{
  widget: WidgetConfig
  onToggle: (id: string) => void
  children?: React.ReactNode
}> = ({ widget, onToggle, children }) => {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: widget.id })

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    background: 'rgba(0, 212, 255, 0.04)',
    border: `1px solid rgba(0, 212, 255, ${isDragging ? '0.6' : '0.2'})`,
    backdropFilter: 'blur(12px)',
    borderRadius: 8,
    padding: '12px 16px',
    cursor: isDragging ? 'grabbing' : 'grab',
    minHeight: 120,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes}>
      {/* Заголовок виджета */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 8,
        }}
        {...listeners}
      >
        <span
          style={{
            fontSize: '0.7rem',
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'var(--hud-accent)',
            textShadow: 'var(--text-glow-cyan)',
            fontFamily: 'var(--font-hud)',
          }}
        >
          {widget.title}
        </span>
        <button
          onClick={(e) => { e.stopPropagation(); onToggle(widget.id) }}
          style={{
            background: 'none',
            border: 'none',
            color: 'var(--hud-text-muted)',
            cursor: 'pointer',
            fontSize: '0.7rem',
            padding: '2px 6px',
          }}
          title="Скрыть виджет"
        >
          ✕
        </button>
      </div>
      {/* Контент виджета */}
      <div style={{ color: 'var(--hud-text)', fontSize: '0.8rem' }}>
        {children ?? (
          <span style={{ color: 'var(--hud-text-muted)' }}>Загрузка...</span>
        )}
      </div>
    </div>
  )
}

// ─── Основной компонент ───────────────────────────────────────────────────────

export const DraggableDashboard: React.FC = () => {
  const [widgets, setWidgets] = useState<WidgetConfig[]>([])
  const [saving, setSaving] = useState(false)

  // Загружаем конфиг при монтировании
  useEffect(() => {
    api.get('/dashboard/config')
      .then((res) => {
        const sorted = [...(res.data.widgets as WidgetConfig[])].sort(
          (a, b) => a.order - b.order
        )
        setWidgets(sorted)
      })
      .catch(() => {
        // Fallback — дефолтные виджеты
        setWidgets([
          { id: 'system',   type: 'system_status', title: 'Статус системы', order: 0, visible: true },
          { id: 'agents',   type: 'agents',         title: 'Агенты',         order: 1, visible: true },
          { id: 'threats',  type: 'threats',         title: 'Угрозы',         order: 2, visible: true },
          { id: 'quotes',   type: 'quotes',          title: 'Котировки',      order: 3, visible: true },
          { id: 'missions', type: 'missions',         title: 'Миссии',         order: 4, visible: true },
        ])
      })
  }, [])

  // Сохраняем конфиг на сервер
  const saveConfig = useCallback(async (updated: WidgetConfig[]) => {
    setSaving(true)
    try {
      await api.put('/dashboard/config', { widgets: updated })
    } catch {
      // Тихо игнорируем — конфиг сохранится при следующей попытке
    } finally {
      setSaving(false)
    }
  }, [])

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  )

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (!over || active.id === over.id) return

    setWidgets((prev) => {
      const oldIndex = prev.findIndex((w) => w.id === active.id)
      const newIndex = prev.findIndex((w) => w.id === over.id)
      const reordered = arrayMove(prev, oldIndex, newIndex).map((w, i) => ({
        ...w,
        order: i,
      }))
      saveConfig(reordered)
      return reordered
    })
  }

  const handleToggle = (id: string) => {
    setWidgets((prev) => {
      const updated = prev.map((w) =>
        w.id === id ? { ...w, visible: !w.visible } : w
      )
      saveConfig(updated)
      return updated
    })
  }

  const visible = widgets.filter((w) => w.visible)
  const hidden = widgets.filter((w) => !w.visible)

  return (
    <div style={{ padding: 16 }}>
      {saving && (
        <div style={{ fontSize: '0.7rem', color: 'var(--hud-text-muted)', marginBottom: 8 }}>
          Сохранение...
        </div>
      )}

      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={visible.map((w) => w.id)} strategy={rectSortingStrategy}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
              gap: 12,
            }}
          >
            {visible.map((widget) => (
              <SortableWidget key={widget.id} widget={widget} onToggle={handleToggle} />
            ))}
          </div>
        </SortableContext>
      </DndContext>

      {/* Скрытые виджеты — кнопки восстановления */}
      {hidden.length > 0 && (
        <div style={{ marginTop: 16, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {hidden.map((w) => (
            <button
              key={w.id}
              onClick={() => handleToggle(w.id)}
              style={{
                background: 'rgba(0,212,255,0.05)',
                border: '1px solid rgba(0,212,255,0.2)',
                color: 'var(--hud-text-dim)',
                borderRadius: 4,
                padding: '4px 10px',
                fontSize: '0.7rem',
                cursor: 'pointer',
              }}
            >
              + {w.title}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
