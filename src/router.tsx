import { createBrowserRouter, Navigate } from 'react-router-dom'
import { AppLayout } from '@/components/Layout/AppLayout'
import { BootPage }      from '@/pages/Boot/BootPage'
import { AuthPage }      from '@/pages/Auth/AuthPage'
import { DashboardPage } from '@/pages/Dashboard/DashboardPage'
import { MemoryPage }    from '@/pages/Memory/MemoryPage'
import { HomePage }      from '@/pages/Home/HomePage'
import { AutonomyPage }  from '@/pages/Autonomy/AutonomyPage'
import { PaymentsPage }  from '@/pages/Payments/PaymentsPage'
import { ProfilePage }   from '@/pages/Profile/ProfilePage'
import { GuardianPage }  from '@/pages/Guardian/GuardianPage'
import { HealthPage }    from '@/pages/Stubs/HealthPage'
import { TwinPage }      from '@/pages/Stubs/TwinPage'
import { RemindersPage } from '@/pages/Stubs/RemindersPage'
import { SocialPage }    from '@/pages/Stubs/SocialPage'
import { MediaPage }     from '@/pages/Stubs/MediaPage'

export const router = createBrowserRouter([
  { path: '/',             element: <Navigate to="/boot" replace /> },
  { path: '/boot',         element: <BootPage /> },
  { path: '/auth/login',   element: <AuthPage /> },
  { path: '/auth/register',element: <AuthPage /> },
  {
    element: <AppLayout />,
    children: [
      { path: '/dashboard', element: <DashboardPage /> },
      { path: '/memory',    element: <MemoryPage />    },
      { path: '/home',      element: <HomePage />      },
      { path: '/autonomy',  element: <AutonomyPage />  },
      { path: '/payments',  element: <PaymentsPage />  },
      { path: '/profile',   element: <ProfilePage />   },
      { path: '/guardian',  element: <GuardianPage />  },
      { path: '/health',    element: <HealthPage />    },
      { path: '/twin',      element: <TwinPage />      },
      { path: '/reminders', element: <RemindersPage /> },
      { path: '/social',    element: <SocialPage />    },
      { path: '/media',     element: <MediaPage />     },
      { path: '*',          element: <Navigate to="/dashboard" replace /> },
    ],
  },
])
