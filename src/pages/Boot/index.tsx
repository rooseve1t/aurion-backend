import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CoreOrb } from '@/components/CoreOrb'

const BOOT_STEPS = [
  'ИНИЦИАЛИЗАЦИЯ ЯДРА...',
  'ЗАГРУЗКА НЕЙРОННЫХ МАТРИЦ...',
  'ПОДКЛЮЧЕНИЕ К КВАНТОВОМУ МОДУЛЮ...',
  'СИНХРОНИЗАЦИЯ ПАМЯТИ...',
  'AURION OS ГОТОВ',
]

export default function BootPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((s) => {
        const next = s + 1
        setProgress(Math.min(100, (next / BOOT_STEPS.length) * 100))
        if (next >= BOOT_STEPS.length) {
          clearInterval(interval)
          setTimeout(() => navigate('/dashboard'), 800)
        }
        return next
      })
    }, 600)
    return () => clearInterval(interval)
  }, [navigate])

  return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center gap-8 p-8">
      <CoreOrb size={120} />

      <div className="text-center space-y-1">
        <div className="text-2xl font-bold tracking-[0.3em] text-cyan">AURION OS</div>
        <div className="text-xs text-cyan/40 tracking-widest">ПЕРСОНАЛЬНЫЙ ИИ-АССИСТЕНТ</div>
      </div>

      {/* Progress bar */}
      <div className="w-64 space-y-2">
        <div className="h-0.5 bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full bg-cyan transition-all duration-500"
            style={{ width: `${progress}%`, boxShadow: '0 0 8px #00e5ff' }}
          />
        </div>
        <div className="text-center text-[10px] text-cyan/60 tracking-widest min-h-[16px]">
          {BOOT_STEPS[step] ?? ''}
        </div>
      </div>

      <div className="text-[9px] text-white/20 tracking-widest">
        AURION INTELLIGENCE SYSTEMS
      </div>
    </div>
  )
}
