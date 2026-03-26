import { Link, useLocation } from 'react-router-dom'

interface NavItem {
  path: string
  label: string
  icon?: string
}

const navItems: NavItem[] = [
  { path: '/', label: 'Overview' },
  { path: '/standings/drivers', label: 'Driver Standings' },
  { path: '/standings/constructors', label: 'Constructor Standings' },
  { path: '/calendar', label: 'Calendar' },
  { path: '/races', label: 'Race Results' },
  { path: '/qualifying', label: 'Qualifying' },
  { path: '/head-to-head', label: 'Head to Head' },
  { path: '/championship', label: 'Championship' },
  { path: '/lap-times', label: 'Lap Times' },
  { path: '/analytics', label: 'Analytics' },
  { path: '/live', label: 'Live Tracker' },
]

export function Sidebar() {
  const location = useLocation()
  
  return (
    <aside className="w-64 bg-transparent border-r border-f1-border min-h-screen">
      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`block px-4 py-2 rounded-md transition-colors ${
                isActive
                  ? 'bg-f1-red text-white'
                  : 'text-gray-300 hover:bg-gray-100'
              }`}
            >
              {item.label}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
