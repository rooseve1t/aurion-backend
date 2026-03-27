import { useEffect, useState } from 'react'
import type { Subscription, Tariff } from '@/types'
import { paymentsService } from '@/services/payments'
import { useAuthStore } from '@/store/authStore'

export function useSubscription() {
  const user = useAuthStore((s) => s.user)
  const [subscription, setSubscription] = useState<(Subscription & { tariff?: Tariff; days_left?: number }) | null>(null)
  const [loading, setLoading] = useState(false)
  const isPrivileged = user?.role === 'creator' || user?.role === 'admin'

  useEffect(() => {
    if (!user) return
    setLoading(true)
    paymentsService.currentSubscription()
      .then(setSubscription)
      .catch(() => setSubscription(null))
      .finally(() => setLoading(false))
  }, [user])

  const hasFeature = (feature: string): boolean => {
    if (isPrivileged) return true
    if (!subscription?.tariff?.features) return false
    return !!subscription.tariff.features[feature]
  }

  const tier = isPrivileged ? 'pro' : subscription?.tariff?.name?.toLowerCase() || 'free'

  return { subscription, loading, hasFeature, tier }
}
