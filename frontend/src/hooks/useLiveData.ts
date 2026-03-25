import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { liveApi } from '../api/live'
import { useWebSocket } from './useWebSocket'
import { useSessionStore } from '../store/sessionStore'
import { useLiveRaceStore } from '../store/liveRaceStore'

/**
 * Hook that combines REST API for initial session data and WebSocket for real-time updates
 * 
 * Flow:
 * 1. Fetch current session info via REST
 * 2. Determine session mode (live, upcoming, replay)
 * 3. If live or replay, connect to WebSocket for real-time updates
 * 4. Handle session mode changes
 */
export const useLiveData = () => {
  const setCurrentSession = useSessionStore((s) => s.setCurrentSession)
  const setSessionMode = useSessionStore((s) => s.setSessionMode)
  const currentSession = useSessionStore((s) => s.currentSession)
  const sessionMode = useSessionStore((s) => s.sessionMode)
  const clearLiveData = useLiveRaceStore((s) => s.clearLiveData)

  // Fetch current session info
  const {
    data: sessionInfo,
    isLoading: isLoadingSession,
    error: sessionError,
    refetch: refetchSession,
  } = useQuery({
    queryKey: ['live', 'session'],
    queryFn: liveApi.getCurrentSession,
    staleTime: 30000, // 30 second stale time for session data
    refetchInterval: sessionMode === 'upcoming' ? 30000 : false, // Poll every 30s in upcoming mode
    retry: 3, // 3 retry attempts
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })

  // Update session store when data changes
  useEffect(() => {
    if (sessionInfo) {
      setCurrentSession(sessionInfo)
      setSessionMode(sessionInfo.mode)
      
      // Reset live data when session changes
      if (currentSession?.session_key !== sessionInfo.session_key) {
        clearLiveData()
      }
    }
  }, [sessionInfo, setCurrentSession, setSessionMode, currentSession, clearLiveData])

  // Connect to WebSocket for live or replay sessions
  const shouldConnectWS = sessionMode === 'live' || sessionMode === 'replay'
  const sessionKey = shouldConnectWS ? currentSession?.session_key || null : null
  
  const { status: wsStatus } = useWebSocket(sessionKey, {
    maxRetries: 5,
    initialRetryDelay: 1000,
    maxRetryDelay: 30000,
  })

  // Fetch initial data for live/replay sessions
  const {
    data: initialPositions,
    isLoading: isLoadingPositions,
  } = useQuery({
    queryKey: ['live', 'positions', sessionKey],
    queryFn: () => liveApi.getLivePositions(sessionKey!),
    enabled: !!sessionKey && shouldConnectWS,
    staleTime: 0, // No caching for live mode data
    gcTime: 0, // No garbage collection time
    retry: 3,
  })

  const {
    data: initialIntervals,
    isLoading: isLoadingIntervals,
  } = useQuery({
    queryKey: ['live', 'intervals', sessionKey],
    queryFn: () => liveApi.getLiveIntervals(sessionKey!),
    enabled: !!sessionKey && shouldConnectWS,
    staleTime: 0, // No caching for live mode data
    gcTime: 0,
    retry: 3,
  })

  const {
    data: initialRaceControl,
    isLoading: isLoadingRaceControl,
  } = useQuery({
    queryKey: ['live', 'racecontrol', sessionKey],
    queryFn: () => liveApi.getRaceControl(sessionKey!),
    enabled: !!sessionKey && shouldConnectWS,
    staleTime: 0, // No caching for live mode data
    gcTime: 0,
    retry: 3,
  })

  // Set initial data in store
  const updatePositions = useLiveRaceStore((s) => s.updatePositions)
  const updateIntervals = useLiveRaceStore((s) => s.updateIntervals)
  const addRaceControlMessage = useLiveRaceStore((s) => s.addRaceControlMessage)

  useEffect(() => {
    if (initialPositions) {
      updatePositions(initialPositions)
    }
  }, [initialPositions, updatePositions])

  useEffect(() => {
    if (initialIntervals) {
      updateIntervals(initialIntervals)
    }
  }, [initialIntervals, updateIntervals])

  useEffect(() => {
    if (initialRaceControl) {
      initialRaceControl.forEach(msg => addRaceControlMessage(msg))
    }
  }, [initialRaceControl, addRaceControlMessage])

  return {
    // Session info
    sessionInfo: currentSession,
    sessionMode,
    isLoadingSession,
    sessionError,
    refetchSession,
    
    // WebSocket status
    wsStatus,
    
    // Initial data loading states
    isLoadingInitialData: isLoadingPositions || isLoadingIntervals || isLoadingRaceControl,
    
    // Overall loading state
    isLoading: isLoadingSession || (shouldConnectWS && (isLoadingPositions || isLoadingIntervals || isLoadingRaceControl)),
  }
}
