import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Home, User } from 'lucide-react'

const TABS = [
  { path: '/feed',    icon: Home,  label: 'Feed' },
  { path: '/profile', icon: User,  label: 'Profile' },
]

export default function BottomNav() {
  const navigate  = useNavigate()
  const { pathname } = useLocation()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 pb-safe">
      <div className="mx-auto max-w-sm">
        <div className="glass-strong mx-4 mb-4 rounded-2xl px-2 py-2 flex">
          {TABS.map(({ path, icon: Icon, label }) => {
            const active = pathname === path
            return (
              <button key={path} onClick={() => navigate(path)}
                className={`flex-1 flex flex-col items-center gap-1 py-2 rounded-xl transition-all duration-200 ${
                  active ? 'text-accent' : 'text-slate-500 hover:text-slate-300'
                }`}>
                <div className={`relative transition-transform duration-200 ${active ? 'scale-110' : ''}`}>
                  <Icon size={20} strokeWidth={active ? 2.5 : 1.8} fill={active ? 'currentColor' : 'none'} />
                  {active && (
                    <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-accent" />
                  )}
                </div>
                <span className={`text-[10px] font-medium ${active ? 'text-accent' : ''}`}>{label}</span>
              </button>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
