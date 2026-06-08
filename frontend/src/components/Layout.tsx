import { NavLink, Outlet } from 'react-router-dom'
import { BarChart2, BookOpen, Calendar, LayoutDashboard, User, Zap } from 'lucide-react'
import { clsx } from 'clsx'

const nav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analytics', label: 'Analytics', icon: BarChart2 },
  { to: '/questions', label: 'Question Bank', icon: BookOpen },
  { to: '/profile', label: 'Profile', icon: User },
  { to: '/schedule', label: 'Schedule', icon: Calendar },
]

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <aside className="w-60 shrink-0 bg-gray-900 flex flex-col py-6 px-4 gap-1">
        {/* Logo */}
        <div className="flex items-center gap-2.5 px-3 mb-8">
          <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center">
            <Zap size={16} className="text-white" />
          </div>
          <span className="font-bold text-white text-base tracking-tight">JobApply</span>
        </div>

        <p className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Menu</p>

        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all',
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white',
              )
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}

        <div className="mt-auto px-3">
          <div className="bg-gray-800 rounded-xl p-3">
            <p className="text-xs font-medium text-gray-300 mb-1">Pro tip</p>
            <p className="text-xs text-gray-500 leading-relaxed">
              Set a schedule to auto-scrape every morning before you wake up.
            </p>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto p-8">
        <Outlet />
      </main>
    </div>
  )
}
