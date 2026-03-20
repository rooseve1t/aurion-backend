import { useEffect, useState } from 'react'
import { Wrench } from 'lucide-react'
import { diyService } from '@/services/diy'
import { useToast } from '@/hooks/useToast'
import styles from './DIYPage.module.css'

export function DIYPage() {
  const toast = useToast()
  const [instructions, setInstructions] = useState<Awaited<ReturnType<typeof diyService.instructions>> | null>(null)
  const [sketches, setSketches] = useState<Awaited<ReturnType<typeof diyService.listSketches>>>([])
  const [form, setForm] = useState({
    name: '',
    device_type: 'sensor',
    board: 'ESP8266',
    protocol: 'mqtt',
    sketch_code: '// setup + loop',
  })

  const loadData = async () => {
    try {
      const [ins, list] = await Promise.all([diyService.instructions(), diyService.listSketches()])
      setInstructions(ins)
      setSketches(list)
    } catch {
      toast.error('Не удалось загрузить DIY-данные')
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const upload = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await diyService.uploadSketch(form)
      toast.success('Скетч загружен')
      setForm({ ...form, name: '', sketch_code: '// setup + loop' })
      await loadData()
    } catch {
      toast.error('Ошибка загрузки скетча')
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <Wrench size={20} color="var(--cyan)" />
        <span className={styles.title}>DIY HUB</span>
      </div>
      {instructions && (
        <div className={styles.card}>
          <div className={styles.sectionTitle}>MQTT: {instructions.mqtt_host}</div>
          {instructions.quickstart.map((step) => <div key={step}>{step}</div>)}
          <div className={styles.mono}>{instructions.example_topics.join('\n')}</div>
        </div>
      )}
      <form className={styles.card} onSubmit={upload}>
        <div className={styles.sectionTitle}>Загрузить скетч</div>
        <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Название" required />
        <input className="input" value={form.device_type} onChange={(e) => setForm({ ...form, device_type: e.target.value })} placeholder="Тип устройства" required />
        <textarea className={styles.textarea} value={form.sketch_code} onChange={(e) => setForm({ ...form, sketch_code: e.target.value })} />
        <button className="btn btn-cyan" type="submit">Загрузить</button>
      </form>
      <div className={styles.card}>
        <div className={styles.sectionTitle}>Мои скетчи</div>
        {sketches.map((row) => (
          <div key={row.id}>#{row.id} {row.name} • {row.device_type} • {row.board}</div>
        ))}
        {sketches.length === 0 && <div>Пока пусто</div>}
      </div>
    </div>
  )
}
