import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Activity, Brain, Lock, Mic, MicOff, Radar, Send, Settings, Shield, Sparkles, Terminal, Users, Wifi, Zap } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useSystemStore } from '@/store/systemStore'
import { useChatStore } from '@/store/chatStore'
import { StatBar } from '@/components/StatBar/StatBar'
import { CoreOrb } from '@/components/CoreOrb/CoreOrb'
import { HUDModule } from '@/components/HUDModule'
import { MetricWidget } from '@/components/MetricWidget'
import { useToast } from '@/hooks/useToast'
import { browserVoice, type VoiceState } from '@/services/browserVoice'
import { formatDate } from '@/utils'
import { InteractiveButton, InteractiveCard } from '@/components/ui/InteractiveComponents'
import { ActivityIndicator, LoadingIcon } from '@/components/ui/AnimatedIcons'
import { DigitalRain } from '@/components/ui/DigitalRain'
import { NeuralHUD } from '@/components/ui/NeuralHUD'
import { QuantumMap } from '@/components/ui/QuantumMap'
import PersonalityMatrix from '@/components/Widgets/PersonalityMatrix'
import SquadDashboard from '@/components/Widgets/SquadDashboard'
import '@/styles/aurion-design-system.css'
import '@/styles/cyberpunk.css'

export function DashboardPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const stats = useSystemStore((s) => s.stats)
  const { messages, isTyping, sendMessage, loadHistory, connect, disconnect } = useChatStore()
  const [input, setInput] = useState('')
  const [voiceState, setVoiceState] = useState<VoiceState>('idle')
  const [isLoading, setIsLoading] = useState(true)
  const [showPersonalityMatrix, setShowPersonalityMatrix] = useState(false)
  const [showSquadDashboard, setShowSquadDashboard] = useState(false)
  const [proactivity] = useState<any[]>([
    { id: 1, type: 'insight', content: 'Обнаружен паттерн: Сэр, вы часто работаете в это время. Подготовить рабочее окружение?', timestamp: new Date() },
    { id: 2, type: 'security', content: 'Квантовый щит активен. Попыток несанкционированного доступа не обнаружено.', timestamp: new Date() }
  ])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const toast = useToast()
  
  useEffect(() => {
    connect()
    loadHistory()
    return () => disconnect()
  }, [connect, loadHistory, disconnect])

  const operatorName = user?.username || 'оператор'
  const timestampLabel = new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date())
  
  const moduleReadiness = Math.min(100, Math.round((((stats?.devices_online || 0) > 0 ? 2 : 1) + ((stats?.memory_entries || 0) > 0 ? 2 : 1) + ((stats?.active_tasks || 0) >= 0 ? 2 : 1) + (stats?.quantum_status === 'online' ? 2 : 1)) / 8 * 100))
  
  const quickAccess = [
    { label: 'Голос', icon: Mic, tone: 'amber', path: '/resonance' },
    { label: 'Миссии', icon: Sparkles, tone: 'amber', path: '/autonomy' },
    { label: 'Метрики', icon: Activity, tone: 'amber', path: '/dashboard' },
    { label: 'Автономность', icon: Cpu, tone: 'amber', path: '/autonomy' },
    { label: 'Задача', icon: Terminal, tone: 'amber', action: () => setShowPersonalityMatrix(true) },
    { label: 'Скан', icon: Radar, tone: 'amber', path: '/guardian' },
    { label: 'Память', icon: Brain, tone: 'amber', path: '/memory' },
    { label: 'Профиль', icon: Users, tone: 'amber', path: '/profile' },
  ]
  
  const currentPersona = [...messages].reverse().find((message) => message.voice_persona)?.voice_persona || 'jarvis'
  const voiceStatusLabel = voiceState === 'listening' ? 'Слушаю...' : voiceState === 'processing' ? 'Анализирую...' : 'Ожидаю команду'

  useEffect(() => {
    const timer = setTimeout(() => setIsLoading(false), 2000)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  const handleSend = () => {
    if (input.trim()) {
      sendMessage(input)
      setInput('')
    }
  }

  const handleVoiceToggle = () => {
    if (voiceState === 'idle') {
      browserVoice.startRecognition({
        onStateChange: (state) => setVoiceState(state),
        onFinal: (text) => {
          sendMessage(text)
        },
        onError: (msg) => {
          toast.error(msg)
          setVoiceState('idle')
        }
      })
    } else {
      browserVoice.stopRecognition()
      setVoiceState('idle')
    }
  }

  if (isLoading) {
    return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-950 text-amber-300 font-mono p-8">
        <LoadingIcon size={64} type="pulse" />
        <div className="text-xl tracking-widest uppercase animate-pulse mt-6">Аутентификация систем...</div>
        <div className="mt-4 w-64 h-1 bg-slate-900 rounded-full overflow-hidden">
          <div className="h-full bg-amber-400 animate-[loading_2s_ease-in-out_infinite]" style={{ width: '40%' }}></div>
        </div>
      </div>
    )
  }

  return (
    <div className="cyber-dashboard selection:bg-amber-400/30">
      <DigitalRain />
      <div className="scanline-effect"></div>
      
      {/* Header */}
      <header className="h-16 border-b border-white/10 flex items-center justify-between px-6 bg-black/40 backdrop-blur-xl z-50 rounded-b-2xl">
        <div className="flex items-center gap-4">
          <div className="p-2 rounded-lg bg-amber-400/10 text-amber-300 shadow-[0_0_15px_rgba(255,179,71,0.25)]">
            <Radar size={20} className="animate-spin-slow" />
          </div>
          <div>
            <h1 className="text-sm font-display tracking-[0.4em] uppercase text-white neon-text">AURION<span className="text-amber-400">_OS</span></h1>
            <div className="flex items-center gap-2 text-[10px] font-mono text-slate-500">
              <span className="flex items-center gap-1"><Wifi size={8} className="text-green-500" /> ONLINE</span>
              <span>•</span>
              <span>{timestampLabel}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="hidden md:flex items-center gap-8">
            <StatBar stats={stats} />
          </div>
          <InteractiveButton variant="secondary" size="sm" className="text-slate-400 hover:text-white quantum-glass">
            <Settings size={18} />
          </InteractiveButton>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden p-4 gap-6">
        {/* Left Sidebar: Intelligence & Stats */}
        <aside className="hidden lg:flex flex-col w-80 gap-6 overflow-y-auto custom-scrollbar">
          <HUDModule title="System Core" subtitle="Readiness Matrix" icon={Radar}>
            <div className="flex items-center justify-between mb-4">
              <div>
                <div className="text-[9px] font-mono uppercase tracking-widest text-slate-500">Module Readiness</div>
                <div className="text-2xl font-display text-white mt-1 tracking-[0.2em]">{moduleReadiness}%</div>
              </div>
              <ActivityIndicator color="var(--amber)" />
            </div>
            <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden mb-4">
              <div className="h-full bg-amber-400 shadow-[0_0_10px_rgba(255,179,71,0.7)] transition-all duration-1000" style={{ width: `${moduleReadiness}%` }}></div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <MetricWidget label="MEMORY" value={stats?.memory_entries || 0} subValue="nodes" />
              <MetricWidget label="TASKS" value={stats?.active_tasks || 0} subValue="active" />
            </div>
          </HUDModule>

          <div className="flex-1 overflow-y-auto pr-2 space-y-4">
            <h4 className="text-[10px] font-mono text-slate-500 uppercase tracking-widest px-1">Quick_Actions</h4>
            <div className="grid grid-cols-2 gap-2">
              {quickAccess.map((item, i) => (
                <InteractiveButton 
                  key={i} 
                  variant="secondary" 
                  size="sm"
                  onClick={() => {
                    if (item.path) navigate(item.path);
                    if (item.action) item.action();
                  }}
                  className="h-20 flex flex-col items-center justify-center gap-2 quantum-glass group"
                >
                  <item.icon size={18} className={`text-${item.tone}-400 group-hover:scale-110 transition-transform`} />
                  <span className="text-[10px] font-mono uppercase tracking-tighter">{item.label}</span>
                </InteractiveButton>
              ))}
            </div>
          </div>
        </aside>

        {/* Center: HUD Visualizer & Chat */}
        <section className="flex-1 flex flex-col gap-6 relative z-10">
          <div className="flex-1 quantum-glass flex flex-col overflow-hidden relative group">
            {/* Holographic Background Effect */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,179,71,0.08),transparent_70%)] pointer-events-none"></div>
            
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
              {messages.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
                  <div className="relative mb-8">
                    <div className="absolute inset-0 animate-ping bg-amber-400/20 rounded-full"></div>
                    <CoreOrb size={120} active={true} />
                  </div>
                  <h3 className="text-lg font-display text-white mb-2">Система ожидает команды</h3>
                  <p className="text-sm max-w-xs text-slate-400">Все контуры синхронизированы. Я готов сопровождать ваш поток работы.</p>
                </div>
              ) : (
                messages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                      <div className="flex items-center gap-2 mb-1 px-1">
                        <span className="text-[9px] font-mono uppercase tracking-widest text-slate-500">
                          {msg.role === 'user' ? operatorName : msg.voice_persona || 'jarvis'}
                        </span>
                        <span className="text-[9px] font-mono text-slate-700">{formatDate(msg.timestamp)}</span>
                      </div>
                      <div className={`
                        p-4 rounded-2xl text-sm leading-relaxed
                        ${msg.role === 'user' 
                          ? 'bg-amber-400 text-slate-950 font-medium rounded-tr-none' 
                          : 'bg-black/60 text-slate-100 border border-amber-400/20 rounded-tl-none backdrop-blur-md shadow-[0_0_15px_rgba(255,179,71,0.14)]'
                        }
                      `}>
                        {msg.content}
                      </div>
                    </div>
                  </div>
                ))
              )}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-black/40 p-3 rounded-2xl rounded-tl-none border border-amber-400/20">
                    <LoadingIcon size={16} type="spinner" color="var(--amber)" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-6 bg-black/60 border-t border-white/10 backdrop-blur-xl">
              <div className="relative flex items-center gap-4">
                <InteractiveButton 
                  onClick={handleVoiceToggle}
                  variant={voiceState === 'listening' ? 'danger' : 'secondary'}
                  size="sm"
                  className={`rounded-xl h-12 w-12 border-white/10 ${voiceState === 'listening' ? 'animate-pulse bg-red-500/20 text-red-400 border-red-500/30' : 'quantum-glass text-amber-300'}`}
                >
                  {voiceState === 'listening' ? <MicOff size={20} /> : <Mic size={20} />}
                </InteractiveButton>
                
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder={voiceState === 'listening' ? 'Слушаю вас...' : "Введите команду или спросите что-то..."}
                    className="w-full h-12 bg-black/40 border border-white/10 rounded-xl px-4 pr-12 text-sm focus:outline-none focus:border-amber-400/60 transition-colors text-white placeholder:text-slate-600 font-sans"
                  />
                  <InteractiveButton 
                    onClick={handleSend}
                    disabled={!input.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-amber-300 disabled:text-slate-700 transition-colors"
                  >
                    <Send size={18} />
                  </InteractiveButton>
                </div>
                <div className="flex items-center gap-2 mt-4 px-1">
                  <span className="text-[10px] font-mono text-slate-500 uppercase tracking-tighter">{voiceStatusLabel}</span>
                  <div className="flex gap-1">
                    {[1, 2, 3, 4].map(i => (
                      <div key={i} className={`w-1 h-1 rounded-full ${voiceState === 'listening' ? 'bg-amber-400 animate-pulse' : 'bg-slate-800'}`}></div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Right Sidebar: Proactivity Feed */}
        <aside className="hidden xl:flex flex-col w-72 gap-6">
          <div className="proactivity-feed custom-scrollbar">
            <h3 className="text-[10px] font-mono text-slate-500 uppercase tracking-widest mb-4 px-2">JARVIS_Insights</h3>
            {proactivity.map((item) => (
              <div key={item.id} className="proactivity-item quantum-glass">
                <div className="flex items-center gap-2 mb-2">
                  {item.type === 'security' ? <Shield size={12} className="text-amber-300" /> : <Sparkles size={12} className="text-amber-300" />}
                  <span className="text-[8px] font-mono text-slate-500 uppercase">{item.type}</span>
                </div>
                <p className="text-[11px] leading-relaxed text-slate-200">{item.content}</p>
                <p className="text-[8px] font-mono text-slate-600 mt-2">{formatDate(item.timestamp.toISOString())}</p>
              </div>
            ))}
          </div>

          <QuantumMap nodes={[]} />

          <InteractiveCard className="p-5 quantum-glass">
             <div className="flex items-center justify-between mb-4">
               <h3 className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Active_Persona</h3>
               <button 
                 onClick={() => setShowPersonalityMatrix(true)}
                 className="p-1 hover:text-amber-300 transition-colors"
                 title="Modify Personality Matrix"
               >
                 <Settings size={12} />
               </button>
             </div>
             <div className="flex flex-col items-center py-2">
               <NeuralHUD active={isTyping || voiceState !== 'idle'} />
               <p className="mt-4 text-xs font-display text-white uppercase tracking-widest neon-text">{currentPersona}</p>
             </div>
          </InteractiveCard>

          <InteractiveCard className="h-48 p-5 quantum-glass mt-auto">
             <div className="flex items-center justify-between mb-4">
               <h3 className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">System_Log</h3>
               <Terminal size={12} className="text-slate-600" />
             </div>
             <div className="text-[10px] font-mono space-y-1.5 text-slate-400 overflow-hidden">
               <p className="text-green-500/80">{" >> "} Quantum Mesh online...</p>
               <p>{" >> "} Encrypting data streams... <span className="text-amber-300">OK</span></p>
               <p>{" >> "} Proactivity Manager... <span className="text-amber-300">ACTIVE</span></p>
               <p className="animate-pulse">{" >> "} Waiting for neural sync_</p>
             </div>
          </InteractiveCard>
        </aside>
      </main>

      {/* Footer Status Bar */}
      <footer className="h-8 border-t border-white/10 bg-black/60 px-4 flex items-center justify-between text-[9px] font-mono text-slate-600 uppercase tracking-widest z-50">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_5px_#22c55e]"></div> System_Normal</span>
          <span>Security_Level: Maximum</span>
          <span>Encryption: Post-Quantum</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Uptime: {formatDate(new Date().toISOString())}</span>
          <span className="text-slate-400">Aurion OS v1.3.0</span>
        </div>
      </footer>

      {/* Personality Matrix Modal */}
      {showPersonalityMatrix && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
          <div className="relative w-full max-w-4xl">
            <button 
              onClick={() => setShowPersonalityMatrix(false)}
              className="absolute -top-12 right-0 text-white/50 hover:text-white flex items-center gap-2 text-xs font-mono uppercase tracking-widest transition-colors"
            >
              Close_Matrix <Terminal size={14} />
            </button>
            <PersonalityMatrix />
          </div>
        </div>
      )}

      {/* Squad Dashboard Modal */}
      {showSquadDashboard && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md p-4">
          <div className="relative w-full max-w-6xl">
            <button 
              onClick={() => setShowSquadDashboard(false)}
              className="absolute -top-12 right-0 text-white/50 hover:text-white flex items-center gap-2 text-xs font-mono uppercase tracking-widest transition-colors"
            >
              Close_Command_Center <Terminal size={14} />
            </button>
            <SquadDashboard />
          </div>
        </div>
      )}
    </div>
  )
}
