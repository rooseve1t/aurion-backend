import { RouterProvider } from 'react-router-dom'
import { router } from './router'
import { ToastContainer } from '@/components/Toast/ToastContainer'
import { AurionEnhanced } from '@/components/AurionEnhanced'

export function App() {
  return (
    <>
      <AurionEnhanced />
      <ToastContainer />
    </>
  )
}
