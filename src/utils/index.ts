import { format, formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'

export const formatDate = (iso: string) =>
  format(new Date(iso), 'dd.MM.yyyy HH:mm', { locale: ru })

export const timeAgo = (iso: string) =>
  formatDistanceToNow(new Date(iso), { addSuffix: true, locale: ru })

export const formatRub = (amount: string | number) =>
  new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 })
    .format(Number(amount))

export const clampText = (text: string, max = 80) =>
  text.length > max ? text.slice(0, max) + '…' : text

export const deviceTypeLabel: Record<string, string> = {
  light: 'Свет',
  switch: 'Выключатель',
  thermostat: 'Термостат',
  lock: 'Замок',
  sensor: 'Сенсор',
}

export const agentTypeLabel: Record<string, string> = {
  financial: 'Финансовый',
  smarthome: 'Умный дом',
  osint: 'OSINT',
  memory: 'Память',
}

export const taskStatusLabel: Record<string, string> = {
  queued: 'В очереди',
  running: 'Выполняется',
  completed: 'Завершено',
  failed: 'Ошибка',
  cancelled: 'Отменено',
}
