import { useState, useMemo, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { liveApi } from '../../api/live'
import type { SessionInfo } from '../../types/live'

interface SessionsByCircuit {
  [circuitName: string]: SessionInfo[]
}

interface SessionsByYear {
  [year: string]: SessionsByCircuit
}

type SessionType = 'all' | 'Race' | 'Qualifying' | 'Practice' | 'Sprint'

export function SessionSelector() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [searchQuery, setSearchQuery] = useState('')
  const [sessionTypeFilter, setSessionTypeFilter] = useState<SessionType>('all')
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear())
  const [focusedIndex, setFocusedIndex] = useState<number>(-1)
  const listRef = useRef<HTMLDivElement>(null)
  
  const currentSessionKey = searchParams.get('session_key')

  // Fetch sessions for selected year
  const { data: sessions, isLoading, error } = useQuery<SessionInfo[]>({
    queryKey: ['sessions', selectedYear],
    queryFn: () => liveApi.getSessionsByYear(selectedYear),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Group sessions by year and circuit
  const groupedSessions = useMemo<SessionsByYear>(() => {
    if (!sessions) return {}

    const filtered = sessions.filter((session) => {
      // Filter by search query (circuit name)
      const matchesSearch = searchQuery === '' || 
        session.circuit_short_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        session.location.toLowerCase().includes(searchQuery.toLowerCase()) ||
        session.country_name.toLowerCase().includes(searchQuery.toLowerCase())

      // Filter by session type
      const matchesType = sessionTypeFilter === 'all' || 
        session.session_type === sessionTypeFilter ||
        (sessionTypeFilter === 'Practice' && session.session_type.includes('Practice'))

      return matchesSearch && matchesType
    })

    const grouped: SessionsByYear = {}

    filtered.forEach((session) => {
      const year = new Date(session.date_start).getFullYear().toString()
      const circuit = session.circuit_short_name

      if (!grouped[year]) {
        grouped[year] = {}
      }

      if (!grouped[year][circuit]) {
        grouped[year][circuit] = []
      }

      grouped[year][circuit].push(session)
    })

    // Sort sessions within each circuit by date (most recent first)
    Object.keys(grouped).forEach((year) => {
      Object.keys(grouped[year]).forEach((circuit) => {
        grouped[year][circuit].sort((a, b) => 
          new Date(b.date_start).getTime() - new Date(a.date_start).getTime()
        )
      })
    })

    return grouped
  }, [sessions, searchQuery, sessionTypeFilter])

  // Get years in descending order
  const years = useMemo(() => {
    return Object.keys(groupedSessions).sort((a, b) => parseInt(b) - parseInt(a))
  }, [groupedSessions])

  // Flatten sessions for keyboard navigation
  const flatSessions = useMemo(() => {
    const flat: SessionInfo[] = []
    years.forEach((year) => {
      Object.keys(groupedSessions[year]).forEach((circuit) => {
        flat.push(...groupedSessions[year][circuit])
      })
    })
    return flat
  }, [years, groupedSessions])

  // Handle session selection
  const handleSelectSession = (sessionKey: string) => {
    setSearchParams({ session_key: sessionKey })
  }

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (flatSessions.length === 0) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setFocusedIndex((prev) => Math.min(prev + 1, flatSessions.length - 1))
          break
        case 'ArrowUp':
          e.preventDefault()
          setFocusedIndex((prev) => Math.max(prev - 1, 0))
          break
        case 'Enter':
          e.preventDefault()
          if (focusedIndex >= 0 && focusedIndex < flatSessions.length) {
            handleSelectSession(flatSessions[focusedIndex].session_key)
          }
          break
        case 'Escape':
          e.preventDefault()
          setFocusedIndex(-1)
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [flatSessions, focusedIndex])

  // Scroll focused item into view
  useEffect(() => {
    if (focusedIndex >= 0 && listRef.current) {
      const focusedElement = listRef.current.querySelector(`[data-index="${focusedIndex}"]`)
      focusedElement?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  }, [focusedIndex])

  // Generate year options (current year and 5 years back)
  const yearOptions = useMemo(() => {
    const currentYear = new Date().getFullYear()
    return Array.from({ length: 6 }, (_, i) => currentYear - i)
  }, [])

  if (isLoading) {
    return (
      <div className="f1-panel p-6">
        <h3 className="text-lg font-semibold mb-4">Select Session</h3>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="f1-panel p-6">
        <h3 className="text-lg font-semibold mb-4">Select Session</h3>
        <div className="text-center py-12 text-red-600">
          Failed to load sessions. Please try again.
        </div>
      </div>
    )
  }

  return (
    <div className="f1-panel">
      <div className="bg-gray-800 text-white px-4 py-3 font-semibold">
        Select Session
      </div>

      <div className="p-4 space-y-4">
        {/* Year selector */}
        <div>
          <label htmlFor="year-select" className="block text-sm font-medium text-gray-300 mb-2">
            Year
          </label>
          <select
            id="year-select"
            value={selectedYear}
            onChange={(e) => setSelectedYear(parseInt(e.target.value))}
            className="w-full px-3 py-2 border border-f1-border rounded-md focus:outline-none focus:ring-2 focus:ring-f1-red"
            aria-label="Select year"
          >
            {yearOptions.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>

        {/* Search input */}
        <div>
          <label htmlFor="circuit-search" className="block text-sm font-medium text-gray-300 mb-2">
            Search Circuit
          </label>
          <input
            id="circuit-search"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by circuit name..."
            className="w-full px-3 py-2 border border-f1-border rounded-md focus:outline-none focus:ring-2 focus:ring-f1-red"
            aria-label="Search circuits"
          />
        </div>

        {/* Session type filter */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Session Type
          </label>
          <div className="flex flex-wrap gap-2">
            {(['all', 'Race', 'Qualifying', 'Sprint', 'Practice'] as SessionType[]).map((type) => (
              <button
                key={type}
                onClick={() => setSessionTypeFilter(type)}
                className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                  sessionTypeFilter === type
                    ? 'bg-f1-red f1-glow text-white'
                    : 'bg-gray-100 text-gray-300 hover:bg-gray-200'
                }`}
                aria-pressed={sessionTypeFilter === type}
                aria-label={`Filter by ${type}`}
              >
                {type === 'all' ? 'All' : type}
              </button>
            ))}
          </div>
        </div>

        {/* Sessions list */}
        <div 
          ref={listRef}
          className="max-h-96 overflow-y-auto border border-f1-border rounded-md"
          role="listbox"
          aria-label="Available sessions"
        >
          {years.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              No sessions found matching your criteria
            </div>
          ) : (
            years.map((year) => (
              <div key={year} className="border-b border-f1-border last:border-b-0">
                <div className="bg-[#292a2c]/40 px-4 py-2 font-semibold text-gray-300 sticky top-0">
                  {year}
                </div>
                {Object.keys(groupedSessions[year]).map((circuit) => (
                  <div key={circuit} className="border-t border-gray-100">
                    <div className="bg-gray-100 px-4 py-2 text-sm font-medium text-gray-400">
                      {circuit}
                    </div>
                    {groupedSessions[year][circuit].map((session, idx) => {
                      const globalIndex = flatSessions.indexOf(session)
                      const isSelected = session.session_key === currentSessionKey
                      const isFocused = globalIndex === focusedIndex

                      return (
                        <button
                          key={session.session_key}
                          data-index={globalIndex}
                          onClick={() => handleSelectSession(session.session_key)}
                          className={`w-full text-left px-4 py-3 transition-colors ${
                            isSelected
                              ? 'bg-blue-100 border-l-4 border-blue-600'
                              : isFocused
                              ? 'bg-gray-100'
                              : 'hover:bg-[#292a2c]/40'
                          }`}
                          role="option"
                          aria-selected={isSelected}
                          tabIndex={isFocused ? 0 : -1}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="font-medium text-f1-white">
                                {session.session_name}
                              </div>
                              <div className="text-sm text-gray-400 mt-1">
                                {new Date(session.date_start).toLocaleDateString('en-US', {
                                  weekday: 'short',
                                  year: 'numeric',
                                  month: 'short',
                                  day: 'numeric',
                                })}
                              </div>
                            </div>
                            <div className="ml-4">
                              <span
                                className={`inline-block px-2 py-1 text-xs font-semibold rounded ${
                                  session.session_type === 'Race'
                                    ? 'bg-red-100 text-red-800'
                                    : session.session_type === 'Qualifying'
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : session.session_type === 'Sprint'
                                    ? 'bg-orange-100 text-orange-800'
                                    : 'bg-gray-100 text-f1-white'
                                }`}
                              >
                                {session.session_type}
                              </span>
                            </div>
                          </div>
                        </button>
                      )
                    })}
                  </div>
                ))}
              </div>
            ))
          )}
        </div>

        {/* Keyboard navigation hint */}
        <div className="text-xs text-gray-400 text-center">
          Use ↑↓ arrow keys to navigate, Enter to select, Esc to clear focus
        </div>
      </div>
    </div>
  )
}
