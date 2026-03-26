import { memo } from 'react'
import { useLiveRaceStore } from '../../store/liveRaceStore'
import type { RaceControlMessage } from '../../types/live'

export const RaceControlFeed = memo(() => {
  const raceControl = useLiveRaceStore((s) => s.raceControl)

  const getFlagIcon = (flag: RaceControlMessage['flag']): string | null => {
    if (!flag) return null
    switch (flag) {
      case 'YELLOW':
        return '🟨'
      case 'RED':
        return '🟥'
      case 'GREEN':
        return '🟩'
      case 'BLUE':
        return '🟦'
      case 'CHEQUERED':
        return '🏁'
      default:
        return null
    }
  }

  const getMessageBackground = (message: RaceControlMessage): string => {
    const lowerMessage = message.message.toLowerCase()
    const lowerCategory = message.category.toLowerCase()
    
    // Highlight red flag messages with red background
    if (message.flag === 'RED' || lowerMessage.includes('red flag')) {
      return 'bg-red-50 border-red-200'
    }
    
    // Highlight safety car messages with yellow background
    if (lowerMessage.includes('safety car') || lowerCategory.includes('safety')) {
      return 'bg-yellow-50 border-yellow-200'
    }
    
    // Highlight DRS messages with green background
    if (lowerMessage.includes('drs') || lowerCategory.includes('drs')) {
      return 'bg-green-50 border-green-200'
    }
    
    return 'bg-transparent border-f1-border'
  }

  const getCategoryBadgeColor = (category: string): string => {
    const lowerCategory = category.toLowerCase()
    if (lowerCategory.includes('flag')) return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    if (lowerCategory.includes('safety')) return 'bg-orange-100 text-orange-800 border-orange-300'
    if (lowerCategory.includes('drs')) return 'bg-green-100 text-green-800 border-green-300'
    if (lowerCategory.includes('track')) return 'bg-blue-100 text-blue-800 border-blue-300'
    return 'bg-gray-100 text-f1-white border-f1-border'
  }

  if (raceControl.length === 0) {
    return (
      <div className="f1-panel p-6">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase mb-4">Race Control</h2>
        <div className="text-center text-gray-400 py-8">
          No race control messages
        </div>
      </div>
    )
  }

  // Sort messages in reverse chronological order (most recent first)
  const sortedMessages = [...raceControl].sort((a, b) => 
    new Date(b.date).getTime() - new Date(a.date).getTime()
  )

  return (
    <div className="f1-panel flex flex-col h-full">
      <div className="p-4 border-b border-f1-border">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase">Race Control</h2>
        <p className="text-sm text-gray-400 mt-1">{raceControl.length} messages</p>
      </div>
      
      <div 
        className="flex-1 overflow-y-auto p-4 space-y-3 max-h-[600px]"
        aria-live="polite"
        aria-atomic="false"
      >
        {sortedMessages.map((msg, index) => {
          const flagIcon = getFlagIcon(msg.flag)
          const categoryColor = getCategoryBadgeColor(msg.category)
          const messageBackground = getMessageBackground(msg)
          
          return (
            <div 
              key={`${msg.date}-${index}`}
              className={`border rounded-lg p-3 hover:shadow-md transition-shadow ${messageBackground}`}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${categoryColor}`}>
                  {flagIcon && <span className="mr-1">{flagIcon}</span>}
                  {msg.category}
                </span>
                <span className="text-xs text-gray-400 whitespace-nowrap">
                  {new Date(msg.date).toLocaleTimeString()}
                </span>
              </div>
              
              <p className="text-sm text-f1-white mb-1">{msg.message}</p>
              
              <div className="flex items-center gap-3 text-xs text-gray-400">
                {msg.lap_number !== null && (
                  <span>Lap {msg.lap_number}</span>
                )}
                {msg.driver_number !== null && (
                  <span>Driver #{msg.driver_number}</span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
})
