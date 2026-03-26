import { useQuery } from '@tanstack/react-query'
import { liveApi } from '../../api/live'
import type { Position, Driver } from '../../types/live'

interface StartingGridProps {
  sessionKey: string
}

interface GridEntry {
  position: number
  driver_number: number
  broadcast_name?: string
  team_name?: string
  team_colour?: string
  qualifying_time?: string
  grid_penalty?: boolean
  original_position?: number
}

export function StartingGrid({ sessionKey }: StartingGridProps) {
  // Fetch starting grid positions
  const { data: gridPositions, isLoading: isLoadingGrid, error: gridError } = useQuery<Position[]>({
    queryKey: ['startingGrid', sessionKey],
    queryFn: () => liveApi.getStartingGrid(sessionKey),
    enabled: !!sessionKey,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Fetch driver information
  const { data: drivers, isLoading: isLoadingDrivers } = useQuery<Driver[]>({
    queryKey: ['drivers', sessionKey],
    queryFn: async () => {
      // Use the API client to fetch drivers
      const response = await fetch(`/api/live/drivers?session_key=${sessionKey}`)
      if (!response.ok) {
        throw new Error('Failed to fetch drivers')
      }
      return response.json()
    },
    enabled: !!sessionKey,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  const isLoading = isLoadingGrid || isLoadingDrivers
  const hasError = gridError

  // Merge grid positions with driver information
  const gridEntries: GridEntry[] = (gridPositions || [])
    .sort((a, b) => a.position - b.position)
    .map((pos) => {
      const driver = drivers?.find((d) => d.driver_number === pos.driver_number)
      
      return {
        position: pos.position,
        driver_number: pos.driver_number,
        broadcast_name: driver?.broadcast_name,
        team_name: driver?.team_name,
        team_colour: driver?.team_colour,
        // TODO: Add qualifying time when available from backend
        qualifying_time: undefined,
        // TODO: Add grid penalty detection when available from backend
        grid_penalty: false,
        original_position: undefined,
      }
    })

  if (isLoading) {
    return (
      <div className="f1-panel p-6">
        <h3 className="text-lg font-semibold mb-4">Starting Grid</h3>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
        </div>
      </div>
    )
  }

  if (hasError || !gridPositions || gridPositions.length === 0) {
    return (
      <div className="f1-panel p-6">
        <h3 className="text-lg font-semibold mb-4">Starting Grid</h3>
        <div className="text-center py-12 text-gray-400">
          Grid not available
        </div>
      </div>
    )
  }

  return (
    <div className="f1-panel">
      <div className="bg-gray-800 text-white px-4 py-3 font-semibold">
        Starting Grid
      </div>
      
      <div className="p-4">
        {/* Grid formation - 2 columns for odd/even positions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {gridEntries.map((entry) => (
            <GridPosition
              key={entry.driver_number}
              entry={entry}
              isPole={entry.position === 1}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

interface GridPositionProps {
  entry: GridEntry
  isPole: boolean
}

function GridPosition({ entry, isPole }: GridPositionProps) {
  return (
    <div
      className={`relative rounded-lg p-4 transition-all ${
        isPole ? 'ring-2 ring-yellow-400 shadow-lg' : 'border border-f1-border'
      }`}
      style={{
        backgroundColor: entry.team_colour ? `#${entry.team_colour}15` : '#f9fafb',
      }}
    >
      {/* Pole position indicator */}
      {isPole && (
        <div className="absolute top-2 right-2">
          <div className="bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded">
            POLE
          </div>
        </div>
      )}

      {/* Grid penalty indicator */}
      {entry.grid_penalty && (
        <div className="absolute top-2 right-2">
          <div className="bg-orange-500 text-white text-xs font-bold px-2 py-1 rounded flex items-center gap-1">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            PENALTY
          </div>
        </div>
      )}

      <div className="flex items-center gap-4">
        {/* Position number */}
        <div className="flex-shrink-0">
          <div className={`text-3xl font-display text-f1-white tracking-wider uppercase ${isPole ? 'text-yellow-600' : 'text-f1-white'}`}>
            P{entry.position}
          </div>
          {entry.grid_penalty && entry.original_position && (
            <div className="text-xs text-gray-400 mt-1">
              (Qualified P{entry.original_position})
            </div>
          )}
        </div>

        {/* Driver info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <div className="text-2xl font-display text-f1-white tracking-wider uppercase text-gray-300">
              {entry.driver_number}
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-semibold text-f1-white truncate">
                {entry.broadcast_name || `Driver ${entry.driver_number}`}
              </div>
              <div className="text-sm text-gray-400 truncate">
                {entry.team_name || 'Unknown Team'}
              </div>
            </div>
          </div>

          {/* Qualifying time */}
          {entry.qualifying_time && (
            <div className="text-sm font-mono text-gray-300 mt-2">
              {entry.qualifying_time}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
