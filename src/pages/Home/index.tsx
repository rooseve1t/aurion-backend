import { useEffect, useState } from 'react'
import { Home as HomeIcon, Zap, Wifi, WifiOff, Lightbulb, Thermometer, Lock, ToggleLeft } from 'lucide-react'
import { useDevicesStore } from '@/store/devicesStore'
import type { Device, DeviceType } from '@/types'

const DEVICE_ICONS: Record<DeviceType, React.ComponentType<{ size?: number; className?: string }>> = {
  light:      Lightbulb,
  thermostat: Thermometer,
  lock:       Lock,
  switch:     ToggleLeft,
  sensor:     Wifi,
}

const DEVICE_COLORS: Record<DeviceType, string> = {
  light:      'text-amber',
  thermostat: 'text-cyan',
  lock:       'text-danger',
  switch:     'text-emerald',
  sensor:     'text-purple',
}

function DeviceCard({ device, onControl }: { device: Device; onControl: (id: number, cmd: Record<string, unknown>) => void }) {
  const Icon = DEVICE_ICONS[device.type] ?? Wifi
  const color = DEVICE_COLORS[device.type] ?? 'text-white'
  const isOn = Boolean(device.state?.on ?? device.state?.locked ?? device.state?.temperature)

  return (
    <div
      className="bg-card border border-white/8 rounded-lg p-4 space-y-3 hover:border-cyan/20 transition-all cursor-pointer group"
      data-testid="device-card"
      onClick={() => onControl(device.id, { on: !isOn })}
    >
      <div className="flex items-start justify-between">
        <Icon size={20} className={device.is_online ? color : 'text-white/20'} />
        <div className={`w-2 h-2 rounded-full ${device.is_online ? 'bg-emerald' : 'bg-white/10'}`} />
      </div>
      <div>
        <div className="text-sm font-medium truncate">{device.name}</div>
        <div className="text-[10px] text-white/30">{device.room || 'Без комнаты'}</div>
      </div>
      <div className="flex items-center justify-between">
        <span className={`text-[10px] tracking-wider ${device.is_online ? color : 'text-white/20'}`}>
          {device.is_online ? 'ONLINE' : 'OFFLINE'}
        </span>
        <div className={`w-8 h-4 rounded-full transition-colors ${isOn ? 'bg-cyan/40' : 'bg-white/10'} relative`}>
          <div className={`absolute top-0.5 w-3 h-3 rounded-full transition-all bg-white ${isOn ? 'left-4' : 'left-0.5'}`} />
        </div>
      </div>
    </div>
  )
}

export default function SmartHomePage() {
  const { devices, loading, fetch, control, optimize } = useDevicesStore()
  const [selectedRoom, setSelectedRoom] = useState<string>('all')
  const [optimizing, setOptimizing] = useState(false)

  useEffect(() => { fetch() }, [])

  const rooms = ['all', ...new Set(devices.map((d) => d.room).filter(Boolean))]
  const filtered = selectedRoom === 'all' ? devices : devices.filter((d) => d.room === selectedRoom)
  const onlineCount = devices.filter((d) => d.is_online).length

  const handleOptimize = async () => {
    setOptimizing(true)
    try { await optimize() }
    finally { setOptimizing(false) }
  }

  return (
    <div className="p-4 max-w-4xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <HomeIcon size={20} className="text-teal" />
          <div>
            <div className="font-bold text-sm tracking-wider">УМНЫЙ ДОМ</div>
            <div className="text-[10px] text-white/30">{onlineCount}/{devices.length} устройств онлайн</div>
          </div>
        </div>
        <button
          onClick={handleOptimize} disabled={optimizing}
          className="flex items-center gap-2 px-3 py-1.5 bg-amber/10 hover:bg-amber/20 border border-amber/30 text-amber text-xs rounded transition-all disabled:opacity-50"
        >
          <Zap size={12} /> {optimizing ? 'Оптимизация...' : 'Оптимизировать'}
        </button>
      </div>

      {/* Rooms filter */}
      <div className="flex gap-2 overflow-x-auto pb-1">
        {rooms.map((room) => (
          <button
            key={room}
            onClick={() => setSelectedRoom(room)}
            className={`px-3 py-1 text-xs rounded-full whitespace-nowrap transition-all ${
              selectedRoom === room
                ? 'bg-teal/20 border border-teal/40 text-teal'
                : 'bg-card border border-white/10 text-white/40 hover:text-white/70'
            }`}
          >
            {room === 'all' ? 'Все' : room}
          </button>
        ))}
      </div>

      {/* Devices grid */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-32 bg-card border border-white/5 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-white/20 text-sm">Нет устройств</div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {filtered.map((device) => (
            <DeviceCard key={device.id} device={device} onControl={control} />
          ))}
        </div>
      )}
    </div>
  )
}
