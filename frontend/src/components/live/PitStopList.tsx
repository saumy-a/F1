import React, { useMemo } from 'react'
import { FixedSizeList } from 'react-window'
import { useLiveRaceStore } from '../../store/liveRaceStore'
import type { PitStop } from '../../types/live'

interface PitStopWithRank extends PitStop {
  driver_name?: string
  rank: number
}

interface PitStopRowProps {
  pitStop: PitStopWithRank
  isFastest: boolean
  isSlowest: boolean
  formatDuration: (duration: number | null) => string
}

const PitStopRow: React.FC<PitStopRowProps> = ({ pitStop, isFastest, isSlowest, formatDuration }) => (
  <div
    className={`flex items-center gap-4 px-4 py-3 border-b hover:bg-[#292a2c]/40 transition-colors ${
      isFastest ? 'bg-green-50' : isSlowest ? 'bg-red-50' : ''
    }`}
  >
    {/* Rank */}
    <div className="w-12 text-center">
      <span className={`inline-block px-2 py-1 rounded text-sm font-semibold ${
        isFastest ? 'bg-green-500 text-white' : isSlowest ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-300'
      }`}>
        #{pitStop.rank}
      </span>
    </div>
    
    {/* Driver name */}
    <div className="flex-1 font-medium">
      {pitStop.driver_name}
    </div>
    
    {/* Lap number */}
    <div className="w-20 text-center text-sm text-gray-400">
      Lap {pitStop.lap_number}
    </div>
    
    {/* Duration */}
    <div className="w-24 text-right font-semibold">
      {formatDuration(pitStop.stop_duration)}
    </div>
  </div>
)

export const PitStopList = React.memo(function PitStopList() {
  const pitStops = useLiveRaceStore((state) => state.pitStops)
  const drivers = useLiveRaceStore((state) => state.drivers)
  
  // Calculate rankings and merge driver data
  const rankedPitStops = useMemo(() => {
    // Filter out pit stops without duration data
    const validPitStops = pitStops.filter((ps) => ps.stop_duration !== null)
    
    // Sort by duration to calculate rankings
    const sortedByDuration = [...validPitStops].sort((a, b) => {
      const durationA = a.stop_duration ?? Infinity
      const durationB = b.stop_duration ?? Infinity
      return durationA - durationB
    })
    
    // Assign ranks
    const rankedStops: PitStopWithRank[] = sortedByDuration.map((ps, index) => {
      const driver = drivers.find((d) => d.driver_number === ps.driver_number)
      return {
        ...ps,
        driver_name: driver?.broadcast_name || `Driver ${ps.driver_number}`,
        rank: index + 1
      }
    })
    
    // Sort by date (most recent first) for display
    return rankedStops.sort((a, b) => {
      return new Date(b.date).getTime() - new Date(a.date).getTime()
    })
  }, [pitStops, drivers])
  
  const fastestRank = 1
  const slowestRank = rankedPitStops.length > 0 ? Math.max(...rankedPitStops.map(ps => ps.rank)) : 0
  
  // Format duration in seconds
  const formatDuration = (duration: number | null): string => {
    if (duration === null) return '—'
    return `${duration.toFixed(3)}s`
  }
  
  // Use virtual scrolling for more than 50 pit stops
  const useVirtualScrolling = rankedPitStops.length > 50
  
  return (
    <div className="f1-panel">
      <div className="bg-gray-800 text-white px-4 py-3 font-semibold flex justify-between items-center">
        <span>Pit Stops</span>
        <span className="text-sm font-normal">Total: {rankedPitStops.length}</span>
      </div>
      
      {useVirtualScrolling ? (
        // Virtual scrolling for large lists
        <FixedSizeList
          height={500}
          itemCount={rankedPitStops.length}
          itemSize={60}
          width="100%"
        >
          {({ index, style }) => {
            const pitStop = rankedPitStops[index]
            const isFastest = pitStop.rank === fastestRank
            const isSlowest = pitStop.rank === slowestRank && rankedPitStops.length > 1
            
            return (
              <div style={style}>
                <PitStopRow
                  pitStop={pitStop}
                  isFastest={isFastest}
                  isSlowest={isSlowest}
                  formatDuration={formatDuration}
                />
              </div>
            )
          }}
        </FixedSizeList>
      ) : (
        // Regular scrolling for smaller lists
        <div className="max-h-[500px] overflow-y-auto">
          {rankedPitStops.map((pitStop, index) => {
            const isFastest = pitStop.rank === fastestRank
            const isSlowest = pitStop.rank === slowestRank && rankedPitStops.length > 1
            
            return (
              <PitStopRow
                key={`${pitStop.driver_number}-${pitStop.lap_number}-${index}`}
                pitStop={pitStop}
                isFastest={isFastest}
                isSlowest={isSlowest}
                formatDuration={formatDuration}
              />
            )
          })}
        </div>
      )}
      
      {rankedPitStops.length === 0 && (
        <div className="px-4 py-8 text-center text-gray-400">
          No pit stops recorded
        </div>
      )}
    </div>
  )
})
