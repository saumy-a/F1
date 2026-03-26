import { Link } from 'react-router-dom'
import { YearSelector } from '../shared/YearSelector'

export function Header() {
  return (
    <header className="bg-f1-black text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="text-2xl font-display text-f1-white tracking-wider uppercase text-f1-red">F1</div>
            <div className="text-xl font-semibold">Dashboard</div>
          </Link>
          
          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link to="/" className="hover:text-f1-red transition-colors">
              Overview
            </Link>
            <Link to="/standings/drivers" className="hover:text-f1-red transition-colors">
              Standings
            </Link>
            <Link to="/calendar" className="hover:text-f1-red transition-colors">
              Calendar
            </Link>
            <Link to="/races" className="hover:text-f1-red transition-colors">
              Races
            </Link>
            <Link to="/analytics" className="hover:text-f1-red transition-colors">
              Analytics
            </Link>
            <Link to="/live" className="hover:text-f1-red transition-colors">
              Live
            </Link>
          </nav>
          
          {/* Year Selector */}
          <div className="flex items-center space-x-4">
            <YearSelector />
          </div>
        </div>
      </div>
    </header>
  )
}
