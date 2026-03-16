import { useState, useEffect } from 'react'
import { Home, Plus, Power, Zap, Thermometer, Lock } from 'lucide-react'
import { smarthomeService } from '@/services/smarthome'
import { useToast } from '@/hooks/useToast'
import type { Device } from '@/types'
import { deviceTypeLabel } from '@/utils'
import styles from './HomePage.module.css'

const DEVICE_ICONS: Record<string, typeof Home> = {
  light: Zap,
  switch: Power,
  thermostat: Thermometer,
  lock: Lock,
  sensor: Home,
}

export function HomePage() {
  const [devices, setDevices]   = useState<Device[]>([])
  const [loading, setLoading]   = useState(false)
  const [optimizing, setOptimizing] = useState(false)
  const [savings, setSavings]   = useState<number | null>(null)
  const [showAdd, setShowAdd]   = useState(false)
  const [newDev, setNewDev]     = useState({ name: '', device_type: 'light', room: 'Гостиная', protocol: 'mqtt' })
  const toast = useToast()

  useEffect(() => {
    setLoading(true)
    smarthomeService.listDevices()
      .then(setDevices)
      .catch(() => toast.error('Ошибка загрузки устройств'))
      .finally(() => setLoading(false))
  }, [])

  const handleControl = async (device: Device, command: string, value?: unknown) => {
    try {
      await smarthomeService.control(device.id, command, value ? { value } : {})
      setDevices((ds) => ds.map((d) =>
        d.id === device.id
          ? { ...d, state: { ...d.state, [command === 'turn_on' ? 'power' : command]: value ?? true } }
          : d
      ))
    } catch { toast.error('Ошибка управления устройством') }
  }

  const handleOptimize = async () => {
    setOptimizing(true)
    try {
      const res = await smarthomeService.optimize()
      setSavings(res.savings_kwh)
      toast.success(`Оптимизировано! Экономия: ${res.savings_kwh} кВт·ч`)
    } catch { toast.error('Ошибка оптимизации') }
    finally { setOptimizing(false) }
  }

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const dev = await smarthomeService.addDevice(newDev)
      setDevices((ds) => [...ds, dev])
      setShowAdd(false)
      toast.success('Устройство добавлено')
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      toast.error(msg || 'Ошибка добавления')
    }
  }

  const rooms = [...new Set(devices.map((d) => d.room))]
  const online = devices.filter((d) => d.is_online).length

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Home size={20} color="var(--cyan)" />
          <span className={styles.title}>УМНЫЙ ДОМ</span>
          <span className={styles.badge}>{online}/{devices.length} онлайн</span>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn btn-ghost" onClick={handleOptimize} disabled={optimizing}>
            <Zap size={14} />
            {optimizing ? 'ОПТИМИЗАЦИЯ...' : 'ОПТИМИЗИРОВАТЬ'}
          </button>
          <button className="btn btn-cyan" onClick={() => setShowAdd(!showAdd)}>
            <Plus size={14} /> УСТРОЙСТВО
          </button>
        </div>
      </div>

      {savings !== null && (
        <div className={styles.savingsBar}>
          ⚡ Квантовая оптимизация: экономия <strong>{savings} кВт·ч</strong> в сутки
        </div>
      )}

      {showAdd && (
        <form className={styles.addForm} onSubmit={handleAdd}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
            <div>
              <label className="label">НАЗВАНИЕ</label>
              <input className="input" value={newDev.name}
                onChange={(e) => setNewDev({ ...newDev, name: e.target.value })} required />
            </div>
            <div>
              <label className="label">ТИП</label>
              <select className="input" value={newDev.device_type}
                onChange={(e) => setNewDev({ ...newDev, device_type: e.target.value })}>
                {Object.entries(deviceTypeLabel).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">КОМНАТА</label>
              <input className="input" value={newDev.room}
                onChange={(e) => setNewDev({ ...newDev, room: e.target.value })} />
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <button type="button" className="btn btn-ghost" onClick={() => setShowAdd(false)}>ОТМЕНА</button>
            <button type="submit" className="btn btn-cyan">ДОБАВИТЬ</button>
          </div>
        </form>
      )}

      {loading && <div className={styles.loading}>ЗАГРУЗКА УСТРОЙСТВ...</div>}

      {!loading && devices.length === 0 && (
        <div className={styles.empty}>
          <Home size={40} color="var(--border)" />
          <p>Нет устройств. Добавьте первое.</p>
        </div>
      )}

      {rooms.map((room) => (
        <div key={room} className={styles.room}>
          <div className={styles.roomTitle}>{room}</div>
          <div className={styles.deviceGrid}>
            {devices.filter((d) => d.room === room).map((dev) => (
              <DeviceCard key={dev.id} device={dev} onControl={handleControl} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function DeviceCard({
  device, onControl,
}: {
  device: Device
  onControl: (d: Device, cmd: string, value?: unknown) => void
}) {
  const Icon = DEVICE_ICONS[device.device_type] || Home
  const isOn = !!(device.state as Record<string, unknown>)?.power

  return (
    <div className={`${styles.deviceCard} ${!device.is_online ? styles.offline : ''}`} data-testid="device-card">
      <div className={styles.devTop}>
        <div className={`${styles.devIcon} ${isOn ? styles.devOn : ''}`}>
          <Icon size={18} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className={styles.devName}>{device.name}</div>
          <div className={styles.devType}>{deviceTypeLabel[device.device_type] || device.device_type}</div>
        </div>
        <div className={`${styles.devStatus} ${device.is_online ? styles.online : ''}`} />
      </div>
      <div className={styles.devControls}>
        {device.device_type !== 'sensor' && (
          <>
            <button
              className={`btn ${isOn ? 'btn-cyan' : 'btn-ghost'}`}
              style={{ fontSize: '10px', padding: '4px 10px' }}
              onClick={() => onControl(device, isOn ? 'turn_off' : 'turn_on')}
              disabled={!device.is_online}
            >
              {isOn ? 'ВЫКЛ' : 'ВКЛ'}
            </button>
          </>
        )}
        {device.device_type === 'thermostat' && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '12px' }}>
            <span style={{ color: 'var(--text-muted)' }}>
              {(device.state as Record<string, unknown>)?.temperature as number || 20}°
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
