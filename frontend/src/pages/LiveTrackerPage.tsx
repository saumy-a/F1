import { lazy, Suspense, memo, useEffect, useState } from 'react'
import { useLiveData } from '../hooks/useLiveData'
import { SessionModeIndicator } from '../components/live/SessionModeIndicator'
import { SessionSelector } from '../components/live/SessionSelector'
import { CircuitInfo } from '../components/live/CircuitInfo'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import { ErrorBoundary } from '../components/shared/ErrorBoundary'
import { useLiveRaceStore } from '../store/liveRaceStore'

const PositionTracker = lazy(() => import('../components/live/PositionTracker').then(m => ({ default: memo(m.PositionTracker) })))
const IntervalDisplay = lazy(() => import('../components/live/IntervalDisplay').then(m => ({ default: memo(m.IntervalDisplay) })))
const TyreStrategyPanel = lazy(() => import('../components/live/TyreStrategyPanel').then(m => ({ default: memo(m.TyreStrategyPanel) })))
const WeatherWidget = lazy(() => import('../components/live/WeatherWidget').then(m => ({ default: memo(m.WeatherWidget) })))
const RaceControlFeed = lazy(() => import('../components/live/RaceControlFeed').then(m => ({ default: memo(m.RaceControlFeed) })))
const TeamRadioPlayer = lazy(() => import('../components/live/TeamRadioPlayer').then(m => ({ default: memo(m.TeamRadioPlayer) })))

export default function LiveTrackerPage() {
  const {
    sessionInfo,
    sessionMode,
    isLoading,
    sessionError,
    refetchSession,
    wsStatus,
    wsRetryCount,
    wsReconnect,
    wsMaxRetries,
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
        <h1 className="text-3xl font-display text-f1-white tracking-wider uppercase mb-6">Live Race Tracker</h1>
        <LoadingSpinner />
      </div>
    )
  }

  if (sessionError) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-display text-f1-white tracking-wider uppercase mb-6">Live Race Tracker</h1>
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
        <h1 className="text-3xl font-display text-f1-white tracking-wider uppercase mb-6">Live Race Tracker</h1>
        <div className="bg-[#292a2c]/40 border border-f1-border rounded-lg p-12 text-center">
          <p className="text-gray-400 text-lg mb-2">No active session</p>
          <p className="text-gray-400 text-sm">Check back during a race weekend for live tracking</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <ErrorBoundary>
        {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-display text-f1-white tracking-wider uppercase mb-2">Live Race Tracker</h1>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl text-gray-300">
              {sessionInfo.session_name} - {sessionInfo.location}
            </h2>
            <p className="text-sm text-gray-400">
              {sessionInfo.circuit_short_name} • {sessionInfo.country_name}
            </p>
          </div>
          <SessionModeIndicator />
        </div>
      </div>

      {/* Upcoming Session View */}
      {sessionMode === 'upcoming' && (
        <div className="space-y-6">
          <div className="f1-panel p-6">
            <CircuitInfo sessionInfo={sessionInfo} />
          </div>
          
          <div className="bg-f1-red/10 border-f1-red/20 border border-f1-red/30 rounded-lg p-8 text-center">
            <h3 className="text-2xl font-display text-f1-white tracking-wider uppercase text-f1-red f1-text-glow mb-4">
              {sessionInfo.session_name}
            </h3>
            <p className="text-f1-red/80 mb-2">
              Session starts: {new Date(sessionInfo.date_start).toLocaleString()}
            </p>
            {countdown && (
              <div className="mt-6">
                <p className="text-sm text-f1-red mb-2">Time until session:</p>
                <p className="text-4xl font-bold text-f1-red f1-text-glow font-mono">{countdown}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Live/Replay Session View */}
      {(sessionMode === 'live' || sessionMode === 'replay') && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 mb-8">
          {/* Replay mode specific: Session Selector atop the layout */}
          {sessionMode === 'replay' && (
            <div className="col-span-1 md:col-span-2 lg:col-span-3">
              <SessionSelector />
            </div>
          )}

          <Suspense fallback={<div className="col-span-1 md:col-span-2 lg:col-span-3"><LoadingSpinner /></div>}>
            {/* Left Column - Positions and Intervals */}
            <div className="col-span-1 md:col-span-2 lg:col-span-2 space-y-4 md:space-y-6">
              <PositionTracker />
              <IntervalDisplay />
              <div className="overflow-x-auto pb-2 touch-pan-x">
                <TyreStrategyPanel />
              </div>
            </div>

            {/* Right Column - Race Control, Weather, and Team Radio */}
            <div className="col-span-1 md:col-span-2 lg:col-span-1 space-y-4 md:space-y-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-1 gap-4 md:gap-6 lg:gap-0">
              <WeatherWidget />
              <RaceControlFeed />
              <div className="md:col-span-2 lg:col-span-1">
                <TeamRadioPlayer />
              </div>
            </div>
          </Suspense>
        </div>
      )}

      {/* Connection Status Footer (for debugging and user feedback) */}
      {(sessionMode === 'live' || sessionMode === 'replay') && (
        <div className="mt-8">
          {wsStatus === 'error' && wsRetryCount >= (wsMaxRetries || 10) && (
            <div className="flex flex-col items-center p-4 bg-red-50 text-red-800 rounded-lg">
              <p className="font-semibold text-sm mb-2">Connection failed after multiple attempts.</p>
              <button 
                onClick={wsReconnect}
                className="px-4 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700 transition"
              >
                Manual Reconnect
              </button>
            </div>
          )}
          
          {wsStatus === 'connecting' && wsRetryCount > 0 && (
            <div className="text-center text-sm font-medium text-amber-600 bg-amber-50 py-2 rounded">
              Reconnecting... (attempt {wsRetryCount})
            </div>
          )}

          {wsStatus === 'connecting' && wsRetryCount === 0 && (
            <div className="text-center text-sm text-gray-400 py-2">
              Connecting to live data...
            </div>
          )}

          {wsStatus === 'connected' && wsRetryCount === 0 && (
            <div className="text-center text-xs text-gray-400 py-2 opacity-70">
              Live Connection Active
            </div>
          )}
        </div>
      )}
      </ErrorBoundary>
    </div>
  )
}
