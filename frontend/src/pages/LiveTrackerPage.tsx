import { useEffect, useState } from 'react'
import { useLiveData } from '../hooks/useLiveData'
import { SessionModeIndicator } from '../components/live/SessionModeIndicator'
import { PositionTracker } from '../components/live/PositionTracker'
import { IntervalDisplay } from '../components/live/IntervalDisplay'
import { RaceControlFeed } from '../components/live/RaceControlFeed'
import { WeatherWidget } from '../components/live/WeatherWidget'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import { useLiveRaceStore } from '../store/liveRaceStore'

export default function LiveTrackerPage() {
  const {
    sessionInfo,
    sessionMode,
    isLoading,
    sessionError,
    refetchSession,
    wsStatus,
  } = useLiveData()

  const clearLiveData = useLiveRaceStore((s) => s.clearLiveData)
  const [countdown, setCountdown] = useState<string | null>(null)

  // Clear live data on component unmount
  useEffect(() => {
    return () => {
      clearLiveData()
    }
  }, [clearLiveData])

  // Calculate countdown for upcoming sessions
  useEffect(() => {
    if (sessionMode === 'upcoming' && sessionInfo?.date_start) {
      const interval = setInterval(() => {
        const now = new Date()
        const start = new Date(sessionInfo.date_start)
        const diff = start.getTime() - now.getTime()

        if (diff <= 0) {
          setCountdown('Session starting soon...')
          return
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24))
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
        const seconds = Math.floor((diff % (1000 * 60)) / 1000)

        if (days > 0) {
          setCountdown(`${days}d ${hours}h ${minutes}m ${seconds}s`)
        } else if (hours > 0) {
          setCountdown(`${hours}h ${minutes}m ${seconds}s`)
        } else {
          setCountdown(`${minutes}m ${seconds}s`)
        }
      }, 1000)

      return () => clearInterval(interval)
    } else {
      setCountdown(null)
    }
  }, [sessionMode, sessionInfo])

  if (isLoading) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">Live Race Tracker</h1>
        <LoadingSpinner />
      </div>
    )
  }

  if (sessionError) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">Live Race Tracker</h1>
        <ErrorMessage
          message={sessionError instanceof Error ? sessionError.message : 'Failed to load session data'}
          onRetry={refetchSession}
        />
      </div>
    )
  }

  if (!sessionInfo) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">Live Race Tracker</h1>
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
          <p className="text-gray-600 text-lg mb-2">No active session</p>
          <p className="text-gray-500 text-sm">Check back during a race weekend for live tracking</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Live Race Tracker</h1>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl text-gray-700">
              {sessionInfo.session_name} - {sessionInfo.location}
            </h2>
            <p className="text-sm text-gray-500">
              {sessionInfo.circuit_short_name} • {sessionInfo.country_name}
            </p>
          </div>
          <SessionModeIndicator />
        </div>
      </div>

      {/* Upcoming Session View */}
      {sessionMode === 'upcoming' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold text-blue-900 mb-4">
            {sessionInfo.session_name}
          </h3>
          <p className="text-blue-700 mb-2">
            Session starts: {new Date(sessionInfo.date_start).toLocaleString()}
          </p>
          {countdown && (
            <div className="mt-6">
              <p className="text-sm text-blue-600 mb-2">Time until session:</p>
              <p className="text-4xl font-bold text-blue-900 font-mono">{countdown}</p>
            </div>
          )}
        </div>
      )}

      {/* Live/Replay Session View */}
      {(sessionMode === 'live' || sessionMode === 'replay') && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Positions and Intervals */}
          <div className="lg:col-span-2 space-y-6">
            <PositionTracker />
            <IntervalDisplay />
          </div>

          {/* Right Column - Race Control and Weather */}
          <div className="space-y-6">
            <WeatherWidget />
            <RaceControlFeed />
          </div>
        </div>
      )}

      {/* Connection Status Footer (for debugging) */}
      {(sessionMode === 'live' || sessionMode === 'replay') && (
        <div className="mt-6 text-center text-xs text-gray-500">
          WebSocket: {wsStatus}
        </div>
      )}
    </div>
  )
}
