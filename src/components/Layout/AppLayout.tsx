import { useEffect } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { useSystemStore } from '@/store/systemStore'
import { SideNav } from './SideNav'
import { BottomNav } from './BottomNav'
import { JarvisHUDOverlay } from '@/components/HUD'
import styles from './AppLayout.module.css'

export function AppLayout() {
  const { user, accessToken, fetchMe } = useAuthStore()
  const fetchStats = useSystemStore((s) => s.fetch)
  const navigate = useNavigate()

  useEffect(() => {
    let cancelled = false

    if (!accessToken) {
      navigate('/auth/login')
      return
    }

    const bootstrap = async () => {
      if (!user) {
        await fetchMe()
      }

      if (!cancelled && localStorage.getItem('access_token')) {
        fetchStats()
      }
    }

    void bootstrap()

    const interval = setInterval(() => {
      if (localStorage.getItem('access_token')) {
        fetchStats()
      }
    }, 30000)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [accessToken, user, fetchMe, fetchStats, navigate])

  if (!accessToken) return null

  return (
    <div className={styles.layout}>
      <div className={styles.aurora} />
      <div className={styles.mesh} />
      <SideNav />
      <main className={styles.main}>
        <Outlet />
      </main>
      <BottomNav />
      <JarvisHUDOverlay />
    </div>
  )
}
