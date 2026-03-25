import { useLiveRaceStore } from '../../store/liveRaceStore'

export const RaceControlFeed = () => {
  const raceControl = useLiveRaceStore((s) => s.raceControl)

  const getCategoryColor = (category: string) => {
    const lowerCategory = category.toLowerCase()
    if (lowerCategory.includes('flag')) return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    if (lowerCategory.includes('safety')) return 'bg-orange-100 text-orange-800 border-orange-300'
    if (lowerCategory.includes('drs')) return 'bg-green-100 text-green-800 border-green-300'
    if (lowerCategory.includes('track')) return 'bg-blue-100 text-blue-800 border-blue-300'
    return 'bg-gray-100 text-gray-800 border-gray-300'
  }

  const getFlagEmoji = (flag: string | null | undefined) => {
    if (!flag) return null
    const flagLower = flag.toLowerCase()
    if (flagLower.includes('green')) return '🟢'
    if (flagLower.includes('yellow')) return '🟡'
    if (flagLower.includes('red')) return '🔴'
    if (flagLower.includes('blue')) return '🔵'
    if (flagLower.includes('chequered') || flagLower.includes('checkered')) return '🏁'
    return '🚩'
  }

  if (raceControl.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Race Control</h2>
        <div className="text-center text-gray-500 py-8">
          No race control messages
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow flex flex-col h-full">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-bold">Race Control</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3 max-h-96">
        {raceControl.map((msg, index) => {
          const flagEmoji = getFlagEmoji(msg.flag)
          const categoryColor = getCategoryColor(msg.category)
          
          return (
            <div 
              key={`${msg.date}-${index}`}
              className="border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${categoryColor}`}>
                  {flagEmoji && <span className="mr-1">{flagEmoji}</span>}
                  {msg.category}
                </span>
                <span className="text-xs text-gray-500 whitespace-nowrap">
                  {new Date(msg.date).toLocaleTimeString()}
                </span>
              </div>
              
              <p className="text-sm text-gray-900 mb-1">{msg.message}</p>
              
              <div className="flex items-center gap-3 text-xs text-gray-500">
                {msg.lap_number && (
                  <span>Lap {msg.lap_number}</span>
                )}
                {msg.driver_number && (
                  <span>Driver #{msg.driver_number}</span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
