import { useMemo } from 'react'
import { useLiveRaceStore } from '../../store/liveRaceStore'

export const IntervalDisplay = () => {
  const positions = useLiveRaceStore((s) => s.positions)
  const intervals = useLiveRaceStore((s) => s.intervals)

  // Merge positions with intervals
  const mergedData = useMemo(() => {
    const intervalMap = new Map(
      intervals.map(i => [i.driver_number, i])
    )
    
    return positions
      .map(pos => ({
        ...pos,
        interval: intervalMap.get(pos.driver_number),
      }))
      .sort((a, b) => a.position - b.position)
  }, [positions, intervals])

  if (mergedData.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Intervals</h2>
        <div className="text-center text-gray-500 py-8">
          No interval data available
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-bold">Intervals</h2>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Pos
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Driver
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Gap to Leader
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Interval
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {mergedData.map((item, index) => (
              <tr 
                key={item.driver_number}
                className={`hover:bg-gray-50 transition-colors ${
                  index === 0 ? 'bg-yellow-50' : ''
                }`}
              >
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className={`text-sm font-bold ${
                    index === 0 ? 'text-yellow-600' : 'text-gray-900'
                  }`}>
                    {item.position}
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    #{item.driver_number}
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-right">
                  <div className="text-sm text-gray-900 font-mono">
                    {index === 0 
                      ? '—' 
                      : item.interval?.gap_to_leader || '—'
                    }
                  </div>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-right">
                  <div className="text-sm text-gray-900 font-mono">
                    {index === 0 
                      ? '—' 
                      : item.interval?.interval || '—'
                    }
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
