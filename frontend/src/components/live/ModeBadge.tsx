import type { SessionMode, SessionInfo } from '../../types/live'

interface ModeBadgeProps {
  mode: SessionMode
  sessionInfo: SessionInfo
}

export function ModeBadge({ mode, sessionInfo }: ModeBadgeProps) {
  const badges = {
    live: {
      bg: 'bg-red-600',
      text: 'text-white',
      label: 'LIVE',
      pulse: true
    },
    upcoming: {
      bg: 'bg-amber-500',
      text: 'text-gray-900',
      label: 'UPCOMING',
      pulse: false
    },
    replay: {
      bg: 'bg-blue-600',
      text: 'text-white',
      label: `REPLAY — ${sessionInfo.circuit_short_name} ${new Date(sessionInfo.date_start).getFullYear()}`,
      pulse: false
    }
  }
  
  const badge = badges[mode]
  
  return (
    <div 
      className={`${badge.bg} ${badge.text} px-4 py-2 rounded-full flex items-center gap-2 sticky top-4 z-50`}
      role="status"
      aria-label={`Session mode: ${badge.label}`}
    >
      {badge.pulse && (
        <span className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-white"></span>
        </span>
      )}
      <span className="font-semibold text-sm">{badge.label}</span>
    </div>
  )
}
