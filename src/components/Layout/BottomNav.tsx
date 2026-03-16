import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Brain, Home, Cpu, User } from 'lucide-react'
import styles from './BottomNav.module.css'

const TABS = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Главная' },
  { to: '/memory',    icon: Brain,           label: 'Память'   },
  { to: '/home',      icon: Home,            label: 'Дом'      },
  { to: '/autonomy',  icon: Cpu,             label: 'Агенты'   },
  { to: '/profile',   icon: User,            label: 'Профиль'  },
]

export function BottomNav() {
  return (
    <nav className={styles.nav}>
      {TABS.map(({ to, icon: Icon, label }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) => `${styles.tab} ${isActive ? styles.active : ''}`}
        >
          <Icon size={18} />
          <span>{label}</span>
        </NavLink>
      ))}
    </nav>
  )
}
