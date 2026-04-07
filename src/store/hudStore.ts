import { create } from 'zustand'
import type { HUDSnapshot } from '@/types'

interface HUDState {
  isVisible: boolean
  isExpanded: boolean
  snapshot: HUDSnapshot | null
  lastUpdated: string | null
  isEmergency: boolean
  emergencyMessage: string
  setSnapshot: (s: HUDSnapshot) => void
  toggleVisibility: () => void
  setExpanded: (v: boolean) => void
  setEmergency: (active: boolean, message?: string) => void
}

export const useHUDStore = create<HUDState>((set) => ({
  isVisible: true,
  isExpanded: false,
  snapshot: null,
  lastUpdated: null,
  isEmergency: false,
  emergencyMessage: '',
  setSnapshot: (s) => set({ snapshot: s, lastUpdated: new Date().toISOString() }),
  toggleVisibility: () => set((state) => ({ isVisible: !state.isVisible })),
  setExpanded: (v) => set({ isExpanded: v }),
  setEmergency: (active, message = '') => set({ isEmergency: active, emergencyMessage: message }),
}))
