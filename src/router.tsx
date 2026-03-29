import React from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from '@/components/Layout/AppLayout'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { BootPage }      from '@/pages/Boot/BootPage'
import { LandingPage }   from '@/pages/Landing/LandingPage'
import { AuthPage }      from '@/pages/Auth/AuthPage'
import { DashboardPage } from '@/pages/Dashboard/DashboardPage'
import { MemoryPage }    from '@/pages/Memory/MemoryPage'
import { HomePage }      from '@/pages/Home/HomePage'
import { AutonomyPage }  from '@/pages/Autonomy/AutonomyPage'
import { PaymentsPage }  from '@/pages/Payments/PaymentsPage'
import { ProfilePage }   from '@/pages/Profile/ProfilePage'
import { GuardianPage }  from '@/pages/Guardian/GuardianPage'
import { DIYPage }       from '@/pages/DIY/DIYPage'
import { HealthPage }    from '@/pages/Stubs/HealthPage'
import { TwinPage }      from '@/pages/Stubs/TwinPage'
import { RemindersPage } from '@/pages/Stubs/RemindersPage'
import { SocialPage }    from '@/pages/Stubs/SocialPage'
import { MediaPage }     from '@/pages/Stubs/MediaPage'
import { NeuralResonance } from '@/pages/NeuralResonance'
import { QuantumVault } from '@/pages/QuantumVault'
import { ARPage } from '@/pages/AR/ARPage'

const wrap = (element: React.ReactElement, name: string) => (
  <ErrorBoundary moduleName={name}>{element}</ErrorBoundary>
)

export const router = createBrowserRouter([
  { path: '/',             element: <LandingPage /> },
  { path: '/boot',         element: <BootPage /> },
  { path: '/auth/login',   element: <AuthPage /> },
  { path: '/auth/register',element: <AuthPage /> },
  {
    element: <AppLayout />,
    children: [
      { path: '/dashboard', element: wrap(<DashboardPage />, 'Dashboard') },
      { path: '/memory',    element: wrap(<MemoryPage />, 'Memory')       },
      { path: '/home',      element: wrap(<HomePage />, 'Home')           },
      { path: '/autonomy',  element: wrap(<AutonomyPage />, 'Autonomy')   },
      { path: '/payments',  element: wrap(<PaymentsPage />, 'Payments')   },
      { path: '/profile',   element: wrap(<ProfilePage />, 'Profile')     },
      { path: '/guardian',  element: wrap(<GuardianPage />, 'Guardian')   },
      { path: '/diy',       element: wrap(<DIYPage />, 'DIY')             },
      { path: '/health',    element: wrap(<HealthPage />, 'Health')       },
      { path: '/twin',      element: wrap(<TwinPage />, 'Twin')           },
      { path: '/reminders', element: wrap(<RemindersPage />, 'Reminders') },
      { path: '/social',    element: wrap(<SocialPage />, 'Social')       },
      { path: '/media',     element: wrap(<MediaPage />, 'Media')         },
      { path: '/resonance', element: wrap(<NeuralResonance />, 'Neural Resonance') },
      { path: '/vault',     element: wrap(<QuantumVault />, 'Quantum Vault') },
      { path: '/ar',        element: wrap(<ARPage />, 'AR')               },
      { path: '*',          element: <Navigate to="/dashboard" replace /> },
    ],
  },
])
