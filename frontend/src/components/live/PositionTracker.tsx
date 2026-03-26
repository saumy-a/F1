import { useMemo } from 'react'
import { useLiveRaceStore } from '../../store/liveRaceStore'

export const PositionTracker = () => {
  const positions = useLiveRaceStore((s) => s.positions)
  const lastUpdate = useLiveRaceStore((s) => s.lastUpdate)

  // Sort positions by position number
  const sortedPositions = useMemo(() => {
    return [...positions].sort((a, b) => a.position - b.position)
  }, [positions])

  if (positions.length === 0) {
    return (
      <div className="f1-panel p-6">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase mb-4">Live Positions</h2>
        <div className="text-center text-gray-400 py-8">
          No position data available
        </div>
      </div>
    )
  }

  return (
    <div className="f1-panel">
      <div className="p-4 border-b border-f1-border flex justify-between items-center">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase">Live Positions</h2>
        {lastUpdate && (
          <span className="text-xs text-gray-400">
            Updated: {new Date(lastUpdate).toLocaleTimeString()}
          </span>
        )}
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-[#292a2c]/40 border-b border-f1-border">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Pos
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Driver
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase tracking-wider">
                Change
              </th>
            </tr>
          </thead>
          <tbody className="bg-transparent divide-y divide-f1-border/50">
            {sortedPositions.map((pos, index) => {
              // Calculate position change (simplified - would need previous state for real change)
              const positionChange = 0 // TODO: Track previous positions for real change calculation
              
              return (
                <tr 
                  key={pos.driver_number}
                  className={`hover:bg-[#292a2c]/40 transition-colors ${
                    index === 0 ? 'bg-yellow-50' : ''
                  }`}
                >
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className={`text-sm font-bold ${
                      index === 0 ? 'text-yellow-600' : 
                      index === 1 ? 'text-gray-400' : 
                      index === 2 ? 'text-orange-600' : 
                      'text-f1-white'
                    }`}>
                      {pos.position}
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-medium text-f1-white">
                        #{pos.driver_number}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap text-center">
                    {positionChange > 0 && (
                      <span className="inline-flex items-center text-green-600 text-sm font-medium">
                        ↑ {positionChange}
                      </span>
                    )}
                    {positionChange < 0 && (
                      <span className="inline-flex items-center text-red-600 text-sm font-medium">
                        ↓ {Math.abs(positionChange)}
                      </span>
                    )}
                    {positionChange === 0 && (
                      <span className="text-gray-400 text-sm">—</span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
