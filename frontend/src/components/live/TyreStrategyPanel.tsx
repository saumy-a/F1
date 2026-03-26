import React, { useMemo } from 'react'
import { useLiveRaceStore } from '../../store/liveRaceStore'
import type { Stint, Driver } from '../../types/live'

// Tire compound colors as per requirements
const COMPOUND_COLORS = {
  SOFT: '#E8002D',
  MEDIUM: '#FFF200',
  HARD: '#CCCCCC',
  INTERMEDIATE: '#43B02A',
  WET: '#0067AD'
} as const

interface DriverStintData {
  driver: Driver
  stints: Stint[]
}

export const TyreStrategyPanel = React.memo(function TyreStrategyPanel() {
  const stints = useLiveRaceStore((state) => state.stints)
  const drivers = useLiveRaceStore((state) => state.drivers)
  
  // Calculate maximum lap number for x-axis scaling
  const maxLap = useMemo(() => {
    if (stints.length === 0) return 60 // Default race length
    
    const maxLapEnd = Math.max(
      ...stints.map((s) => s.lap_end || s.lap_start)
    )
    return Math.max(maxLapEnd, 60)
  }, [stints])
  
  // Group stints by driver and sort by driver number
  const driverStintData = useMemo(() => {
    const data: DriverStintData[] = drivers
      .map((driver) => ({
        driver,
        stints: stints
          .filter((s) => s.driver_number === driver.driver_number)
          .sort((a, b) => a.stint_number - b.stint_number)
      }))
      .sort((a, b) => a.driver.driver_number - b.driver.driver_number)
    
    return data
  }, [drivers, stints])
  
  // Calculate stint length
  const getStintLength = (stint: Stint): number => {
    const lapEnd = stint.lap_end || maxLap
    return lapEnd - stint.lap_start + 1
  }
  
  // Calculate position and width for stint bar
  const getStintBarStyle = (stint: Stint) => {
    const lapEnd = stint.lap_end || maxLap
    const left = (stint.lap_start / maxLap) * 100
    const width = ((lapEnd - stint.lap_start + 1) / maxLap) * 100
    
    return {
      left: `${left}%`,
      width: `${width}%`,
      backgroundColor: COMPOUND_COLORS[stint.compound]
    }
  }
  
  return (
    <div className="f1-panel">
      <div className="bg-gray-800 text-white px-4 py-3 font-semibold">
        Tyre Strategy
      </div>
      
      <div className="p-4">
        {/* X-axis lap numbers */}
        <div className="flex items-center mb-2">
          <div className="w-16 flex-shrink-0" /> {/* Space for driver names */}
          <div className="flex-1 relative h-6">
            <div className="absolute inset-0 flex justify-between text-xs text-gray-400">
              {Array.from({ length: Math.min(11, maxLap + 1) }, (_, i) => {
                const lap = Math.floor((i * maxLap) / 10)
                return (
                  <span key={i} className="text-center">
                    {lap}
                  </span>
                )
              })}
            </div>
          </div>
        </div>
        
        {/* Driver stint bars */}
        <div className="space-y-2 overflow-x-auto">
          {driverStintData.map(({ driver, stints: driverStints }) => (
            <div key={driver.driver_number} className="flex items-center">
              {/* Driver name acronym */}
              <div className="w-16 flex-shrink-0 text-sm font-semibold text-gray-300">
                {driver.name_acronym}
              </div>
              
              {/* Stint bars container */}
              <div className="flex-1 relative h-8 bg-gray-100 rounded">
                {driverStints.map((stint) => {
                  const stintLength = getStintLength(stint)
                  
                  return (
                    <div
                      key={`${driver.driver_number}-${stint.stint_number}`}
                      className="absolute h-full rounded border border-f1-border cursor-pointer hover:opacity-80 transition-opacity"
                      style={getStintBarStyle(stint)}
                      title={`${stint.compound} - ${stintLength} laps (Age: ${stint.tyre_age_at_start})`}
                    >
                      {/* Display stint length if bar is wide enough */}
                      <div className="h-full flex items-center justify-center text-xs font-semibold text-f1-white">
                        {stintLength > 3 && stintLength}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
        
        {driverStintData.length === 0 && (
          <div className="py-8 text-center text-gray-400">
            No tyre strategy data available
          </div>
        )}
        
        {/* Legend */}
        {driverStintData.length > 0 && (
          <div className="mt-4 pt-4 border-t flex flex-wrap gap-4 justify-center text-sm">
            {Object.entries(COMPOUND_COLORS).map(([compound, color]) => (
              <div key={compound} className="flex items-center gap-2">
                <div
                  className="w-4 h-4 rounded border border-f1-border"
                  style={{ backgroundColor: color }}
                />
                <span className="text-gray-300">{compound}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
})
