import React from 'react'
import { useLiveRaceStore } from '../../store/liveRaceStore'

interface RaceEntry {
  driver_number: number
  position: number
  broadcast_name?: string
  team_name?: string
  team_colour?: string
  gap_to_leader?: number | string | null
  interval?: number | string | null
  current_compound?: 'SOFT' | 'MEDIUM' | 'HARD' | 'INTERMEDIATE' | 'WET'
  tire_age?: number
}

function TireIndicator({ compound }: { compound?: string }) {
  const colors = {
    SOFT: 'bg-red-500',
    MEDIUM: 'bg-yellow-400',
    HARD: 'bg-gray-400',
    INTERMEDIATE: 'bg-green-500',
    WET: 'bg-blue-500'
  }
  
  return (
    <div 
      className={`w-6 h-6 rounded-full ${compound ? colors[compound as keyof typeof colors] || 'bg-gray-300' : 'bg-gray-300'}`}
      title={compound || 'Unknown'}
    />
  )
}

export const RaceTower = React.memo(function RaceTower() {
  const positions = useLiveRaceStore((state) => state.positions)
  const intervals = useLiveRaceStore((state) => state.intervals)
  const drivers = useLiveRaceStore((state) => state.drivers)
  const stints = useLiveRaceStore((state) => state.stints)
  
  // Merge position, interval, driver, and stint data for each driver
  const raceOrder: RaceEntry[] = positions
    .sort((a, b) => a.position - b.position)
    .map((pos) => {
      const interval = intervals.find((i) => i.driver_number === pos.driver_number)
      const driver = drivers.find((d) => d.driver_number === pos.driver_number)
      const currentStint = stints.find((s) => s.driver_number === pos.driver_number && s.lap_end === null)
      
      return { 
        driver_number: pos.driver_number,
        position: pos.position,
        broadcast_name: driver?.broadcast_name,
        team_name: driver?.team_name,
        team_colour: driver?.team_colour,
        gap_to_leader: interval?.gap_to_leader,
        interval: interval?.interval,
        current_compound: currentStint?.compound,
        tire_age: currentStint?.tyre_age_at_start
      }
    })
  
  // Format gap/interval display - preserve "+1 LAP" format for lapped cars
  const formatGap = (value: number | string | null | undefined, isP1: boolean): string => {
    if (isP1) return '—'
    if (value === null || value === undefined) return '—'
    if (typeof value === 'string') return value // Preserve "+1 LAP" format
    return `+${value.toFixed(3)}s`
  }
  
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="bg-gray-800 text-white px-4 py-3 font-semibold">
        Race Tower
      </div>
      
      <div className="divide-y">
        {raceOrder.map((entry) => (
          <div
            key={entry.driver_number}
            className="flex items-center gap-4 px-4 py-3 hover:bg-gray-50 transition-colors"
          >
            {/* Position */}
            <div className="w-8 text-center font-bold text-lg">
              {entry.position}
            </div>
            
            {/* Driver number */}
            <div className="w-10 text-center font-semibold text-gray-700">
              {entry.driver_number}
            </div>
            
            {/* Driver info with team color background */}
            <div
              className="flex-1 px-3 py-2 rounded"
              style={{ backgroundColor: entry.team_colour ? `#${entry.team_colour}20` : '#f3f4f6' }}
            >
              <div className="font-semibold">{entry.broadcast_name || `Driver ${entry.driver_number}`}</div>
              <div className="text-sm text-gray-600">{entry.team_name || 'Unknown Team'}</div>
            </div>
            
            {/* Gap to leader */}
            <div className="w-24 text-right text-sm font-medium">
              {formatGap(entry.gap_to_leader, entry.position === 1)}
            </div>
            
            {/* Interval to car ahead */}
            <div className="w-24 text-right text-sm text-gray-600">
              {entry.position === 1 ? '—' : formatGap(entry.interval, false)}
            </div>
            
            {/* Tire info */}
            <div className="flex items-center gap-2 w-32">
              <TireIndicator compound={entry.current_compound} />
              <span className="text-sm">
                {entry.tire_age !== undefined ? `${entry.tire_age} laps` : '— laps'}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      {raceOrder.length === 0 && (
        <div className="px-4 py-8 text-center text-gray-500">
          No race data available
        </div>
      )}
    </div>
  )
})
