import { useSessionStore } from '../../store/sessionStore'

export const SessionModeIndicator = () => {
  const sessionMode = useSessionStore((s) => s.sessionMode)
  const connectionStatus = useSessionStore((s) => s.connectionStatus)

  if (!sessionMode) {
    return (
      <div className="bg-gray-100 border border-gray-300 rounded-lg px-4 py-2 inline-flex items-center gap-2">
        <div className="w-3 h-3 rounded-full bg-gray-400"></div>
        <span className="text-sm font-medium text-gray-600">No Active Session</span>
      </div>
    )
  }

  const modeConfig = {
    live: {
      color: 'bg-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-300',
      textColor: 'text-red-700',
      label: 'LIVE',
      pulse: true,
    },
    upcoming: {
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-300',
      textColor: 'text-blue-700',
      label: 'UPCOMING',
      pulse: false,
    },
    replay: {
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-300',
      textColor: 'text-yellow-700',
      label: 'REPLAY',
      pulse: false,
    },
  }

  const config = modeConfig[sessionMode]

  const statusConfig = {
    connecting: { icon: '⟳', text: 'Connecting...' },
    connected: { icon: '✓', text: 'Connected' },
    disconnected: { icon: '✕', text: 'Disconnected' },
    error: { icon: '⚠', text: 'Error' },
  }

  const statusInfo = statusConfig[connectionStatus]

  return (
    <div className="flex items-center gap-4">
      {/* Session Mode Badge */}
      <div className={`${config.bgColor} border ${config.borderColor} rounded-lg px-4 py-2 inline-flex items-center gap-2`}>
        <div className="relative">
          <div className={`w-3 h-3 rounded-full ${config.color}`}></div>
          {config.pulse && (
            <div className={`absolute inset-0 w-3 h-3 rounded-full ${config.color} animate-ping opacity-75`}></div>
          )}
        </div>
        <span className={`text-sm font-bold ${config.textColor}`}>{config.label}</span>
      </div>

      {/* Connection Status (only show for live/replay) */}
      {(sessionMode === 'live' || sessionMode === 'replay') && (
        <div className="text-sm text-gray-600 flex items-center gap-1">
          <span>{statusInfo.icon}</span>
          <span>{statusInfo.text}</span>
        </div>
      )}
    </div>
  )
}
