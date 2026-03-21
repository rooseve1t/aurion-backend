import { useEffect } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useSystemStore } from '@/store/systemStore'
import { SideNav } from './SideNav'
import { BottomNav } from './BottomNav'
import styles from './AppLayout.module.css'

export function AppLayout() {
  const { user, accessToken, fetchMe } = useAuthStore()
  const fetchStats = useSystemStore((s) => s.fetch)
  const navigate = useNavigate()

  useEffect(() => {
    if (!accessToken) { navigate('/auth/login'); return }
    if (!user) fetchMe()
    fetchStats()
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [accessToken, user, fetchMe, fetchStats, navigate])

  if (!accessToken) return null

  return (
    <div className={styles.layout}>
      <SideNav />
      <main className={styles.main}>
        <Outlet />
      </main>
      <BottomNav />
    </div>
  )
}
