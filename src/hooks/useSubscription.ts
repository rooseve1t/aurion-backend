import { useEffect, useState } from 'react'
import type { Subscription, Tariff } from '@/types'
import { paymentsService } from '@/services/payments'
import { useAuthStore } from '@/store/authStore'

export function useSubscription() {
  const user = useAuthStore((s) => s.user)
  const [subscription, setSubscription] = useState<(Subscription & { tariff?: Tariff; days_left?: number }) | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!user) return
    setLoading(true)
    paymentsService.currentSubscription()
      .then(setSubscription)
      .catch(() => setSubscription(null))
      .finally(() => setLoading(false))
  }, [user])

  const hasFeature = (feature: string): boolean => {
    if (!subscription?.tariff?.features) return false
    return !!subscription.tariff.features[feature]
  }

  const tier = subscription?.tariff?.name?.toLowerCase() || 'free'

  return { subscription, loading, hasFeature, tier }
}
