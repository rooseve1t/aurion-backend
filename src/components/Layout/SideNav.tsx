import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, Brain, Home, Shield, Users, Cpu,
  CreditCard, User, LogOut, Lock
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useSubscription } from '@/hooks/useSubscription'
import { useToast } from '@/hooks/useToast'
import { CoreOrb } from '@/components/CoreOrb/CoreOrb'
import styles from './SideNav.module.css'

const NAV = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Главная',   feature: null },
  { to: '/memory',    icon: Brain,           label: 'Память',     feature: null },
  { to: '/home',      icon: Home,            label: 'Умный дом',  feature: null },
  { to: '/autonomy',  icon: Cpu,             label: 'Агенты',     feature: 'agents' },
  { to: '/guardian',  icon: Shield,          label: 'Защита',     feature: null },
  { to: '/payments',  icon: CreditCard,      label: 'Подписка',   feature: null },
  { to: '/profile',   icon: User,            label: 'Профиль',    feature: null },
]

export function SideNav() {
  const { logout, user } = useAuthStore()
  const { hasFeature } = useSubscription()
  const { warning } = useToast()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/auth/login')
  }

  const handleNav = (e: React.MouseEvent, feature: string | null, to: string) => {
    if (feature && !hasFeature(feature)) {
      e.preventDefault()
      warning(`Требуется Pro-подписка для доступа к этому модулю`)
    }
  }

  return (
    <nav className={styles.nav}>
      {/* Logo */}
      <div className={styles.logo}>
        <CoreOrb size={36} />
        <div className={styles.logoText}>
          <span className={styles.logoMain}>AURION</span>
          <span className={styles.logoSub}>OS v1.0</span>
        </div>
      </div>

      {/* Links */}
      <ul className={styles.links}>
        {NAV.map(({ to, icon: Icon, label, feature }) => {
          const locked = !!(feature && !hasFeature(feature))
          return (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) =>
                  `${styles.link} ${isActive ? styles.active : ''} ${locked ? styles.locked : ''}`
                }
                onClick={(e) => handleNav(e, feature, to)}
              >
                <Icon size={16} />
                <span>{label}</span>
                {locked && <Lock size={10} className={styles.lockIcon} />}
              </NavLink>
            </li>
          )
        })}
      </ul>

      {/* Footer */}
      <div className={styles.footer}>
        <div className={styles.userInfo}>
          <span className={styles.userEmail}>{user?.email}</span>
          <span className={styles.userRole}>{user?.role?.toUpperCase()}</span>
        </div>
        <button className={styles.logoutBtn} onClick={handleLogout} title="Выйти">
          <LogOut size={14} />
        </button>
      </div>
    </nav>
  )
}
