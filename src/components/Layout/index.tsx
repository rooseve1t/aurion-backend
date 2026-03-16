import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Mic, Brain, Shield, Home, Heart,
  Bell, User, Cpu, Share2, Film, Menu, X, LogOut,
  CreditCard, ChevronRight, Lock,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useUiStore } from '@/store/uiStore'
import { useSubscriptionStore } from '@/store/subscriptionStore'
import toast from 'react-hot-toast'

interface NavItem {
  id: string
  label: string
  icon: React.ComponentType<{ size?: number; className?: string }>
  path: string
  feature?: string
}

const NAV_ITEMS: NavItem[] = [
  { id: 'dashboard', label: 'Главная',      icon: LayoutDashboard, path: '/dashboard' },
  { id: 'voice',     label: 'Голос',         icon: Mic,             path: '/voice' },
  { id: 'memory',    label: 'Память',        icon: Brain,           path: '/memory' },
  { id: 'guardian',  label: 'Защита',        icon: Shield,          path: '/guardian' },
  { id: 'home',      label: 'Умный дом',     icon: Home,            path: '/home' },
  { id: 'health',    label: 'Здоровье',      icon: Heart,           path: '/health' },
  { id: 'reminders', label: 'Напоминания',   icon: Bell,            path: '/reminders' },
  { id: 'twin',      label: 'Двойник',       icon: User,            path: '/twin' },
  { id: 'autonomy',  label: 'Автономия',     icon: Cpu,             path: '/autonomy',  feature: 'agents' },
  { id: 'social',    label: 'Соц. связи',    icon: Share2,          path: '/social' },
  { id: 'media',     label: 'Медиа',         icon: Film,            path: '/media' },
]

interface LayoutProps { children: React.ReactNode }

export function Layout({ children }: LayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { sidebarOpen, setSidebarOpen } = useUiStore()
  const { current: subscription } = useSubscriptionStore()
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 480)

  useEffect(() => {
    const onResize = () => setIsMobile(window.innerWidth <= 480)
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  const hasFeature = (feature?: string): boolean => {
    if (!feature) return true
    const features = subscription?.tariff?.features
    if (!features) return false
    return Boolean(features[feature as keyof typeof features])
  }

  const handleNav = (item: NavItem) => {
    if (item.feature && !hasFeature(item.feature)) {
      toast.error('Требуется Pro-подписка', { icon: '🔒' })
      return
    }
    navigate(item.path)
    setSidebarOpen(false)
  }

  const handleLogout = async () => {
    await logout()
    navigate('/auth/login')
  }

  const activeId = NAV_ITEMS.find((n) => location.pathname.startsWith(n.path))?.id

  return (
    <div className="flex h-screen bg-bg text-white font-mono overflow-hidden">
      {/* Sidebar — desktop */}
      <aside className={`
        fixed top-0 left-0 h-full z-40 flex flex-col
        bg-card border-r border-cyan/10 transition-all duration-300
        ${isMobile ? (sidebarOpen ? 'w-64 translate-x-0' : '-translate-x-full') : 'w-56'}
      `}>
        {/* Logo */}
        <div className="p-4 border-b border-cyan/10 flex items-center justify-between">
          <div>
            <div className="text-cyan font-bold text-lg tracking-widest">AURION</div>
            <div className="text-[10px] text-cyan/50 tracking-widest">OS v1.0</div>
          </div>
          {isMobile && (
            <button onClick={() => setSidebarOpen(false)} className="text-cyan/50 hover:text-cyan">
              <X size={18} />
            </button>
          )}
        </div>

        {/* Nav */}
        <nav className="flex-1 overflow-y-auto py-2 scrollbar-thin">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon
            const locked = Boolean(item.feature) && !hasFeature(item.feature)
            const active = activeId === item.id
            return (
              <button
                key={item.id}
                onClick={() => handleNav(item)}
                className={`
                  w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-all
                  ${active
                    ? 'text-cyan bg-cyan/10 border-r-2 border-cyan'
                    : 'text-white/60 hover:text-white hover:bg-white/5'}
                  ${locked ? 'opacity-50' : ''}
                `}
              >
                <Icon size={16} className={active ? 'text-cyan' : ''} />
                <span className="flex-1 text-left">{item.label}</span>
                {locked && <Lock size={12} className="text-amber" />}
                {active && !locked && <ChevronRight size={12} className="text-cyan" />}
              </button>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-cyan/10 p-3 space-y-1">
          <button
            onClick={() => { navigate('/profile'); setSidebarOpen(false) }}
            className="w-full flex items-center gap-3 px-3 py-2 text-sm text-white/60 hover:text-white hover:bg-white/5 rounded"
          >
            <User size={14} />
            <span className="truncate">{user?.username ?? 'Профиль'}</span>
          </button>
          <button
            onClick={() => { navigate('/payments'); setSidebarOpen(false) }}
            className="w-full flex items-center gap-3 px-3 py-2 text-sm text-white/60 hover:text-white hover:bg-white/5 rounded"
          >
            <CreditCard size={14} />
            <span>{subscription?.tariff?.name ?? 'Free'}</span>
          </button>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 text-sm text-danger/70 hover:text-danger hover:bg-danger/10 rounded"
          >
            <LogOut size={14} />
            <span>Выйти</span>
          </button>
        </div>
      </aside>

      {/* Overlay */}
      {isMobile && sidebarOpen && (
        <div className="fixed inset-0 bg-black/60 z-30" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main */}
      <main className={`flex-1 flex flex-col overflow-hidden transition-all ${!isMobile ? 'ml-56' : ''}`}>
        {/* Top bar */}
        <header className="h-12 flex items-center justify-between px-4 border-b border-cyan/10 bg-card/50 backdrop-blur flex-shrink-0">
          {isMobile && (
            <button onClick={() => setSidebarOpen(true)} className="text-cyan/70 hover:text-cyan">
              <Menu size={20} />
            </button>
          )}
          <div className="flex-1" />
          <div className="flex items-center gap-2 text-xs text-cyan/40">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald animate-pulse" />
            ONLINE
          </div>
        </header>

        <div className="flex-1 overflow-auto">{children}</div>
      </main>

      {/* Mobile bottom nav */}
      {isMobile && (
        <nav className="fixed bottom-0 left-0 right-0 bg-card border-t border-cyan/10 z-20 flex">
          {NAV_ITEMS.slice(0, 5).map((item) => {
            const Icon = item.icon
            const active = activeId === item.id
            return (
              <button
                key={item.id}
                onClick={() => handleNav(item)}
                className={`flex-1 flex flex-col items-center py-2 text-[10px] gap-1 ${
                  active ? 'text-cyan' : 'text-white/40'
                }`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>
      )}
    </div>
  )
}
