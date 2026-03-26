import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
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
  const [searchParams] = useSearchParams()
  const sessionKeyFromUrl = searchParams.get('session_key')

  const setCurrentSession = useSessionStore((s) => s.setCurrentSession)
  const setSessionMode = useSessionStore((s) => s.setSessionMode)
  const currentSession = useSessionStore((s) => s.currentSession)
  const sessionMode = useSessionStore((s) => s.sessionMode)
  const clearLiveData = useLiveRaceStore((s) => s.clearLiveData)

  // Fetch current session info or a specific session if session_key is provided
  const {
    data: sessionInfo,
    isLoading: isLoadingSession,
    error: sessionError,
    refetch: refetchSession,
  } = useQuery({
    queryKey: ['live', 'session', sessionKeyFromUrl],
    queryFn: () => 
      sessionKeyFromUrl 
        ? liveApi.getSessionByKey(sessionKeyFromUrl) 
        : liveApi.getCurrentSession(),
    staleTime: 30000, // 30 second stale time for session data
    refetchInterval: (query) => {
      // Poll every 30s in upcoming mode if there is no hard sessionKey (since hard session keys are probably replays anyways)
      return query.state.data?.mode === 'upcoming' && !sessionKeyFromUrl ? 30000 : false
    },
    retry: 3, // 3 retry attempts
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })

  // Update session store when data changes
  useEffect(() => {
    if (sessionInfo) {
      setCurrentSession(sessionInfo)
      // Force replay mode if we are explicitly looking at an old session, even if it might technically evaluate otherwise due to data.
      // But determine_session_mode handles replay nicely.
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
  
  const { status: wsStatus, retryCount, reconnect, maxRetries } = useWebSocket(sessionKey, {
    maxRetries: 10,
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
    staleTime: sessionMode === 'replay' ? Infinity : 0, 
    gcTime: sessionMode === 'replay' ? Infinity : 0,
    retry: 3,
  })

  const {
    data: initialIntervals,
    isLoading: isLoadingIntervals,
  } = useQuery({
    queryKey: ['live', 'intervals', sessionKey],
    queryFn: () => liveApi.getLiveIntervals(sessionKey!),
    enabled: !!sessionKey && shouldConnectWS,
    staleTime: sessionMode === 'replay' ? Infinity : 0,
    gcTime: sessionMode === 'replay' ? Infinity : 0,
    retry: 3,
  })

  const {
    data: initialRaceControl,
    isLoading: isLoadingRaceControl,
  } = useQuery({
    queryKey: ['live', 'racecontrol', sessionKey],
    queryFn: () => liveApi.getRaceControl(sessionKey!),
    enabled: !!sessionKey && shouldConnectWS,
    staleTime: sessionMode === 'replay' ? Infinity : 0,
    gcTime: sessionMode === 'replay' ? Infinity : 0,
    retry: 3,
  })
  
  const {
    data: initialStints,
    isLoading: isLoadingStints,
  } = useQuery({
    queryKey: ['live', 'stints', sessionKey],
    queryFn: () => liveApi.getLiveStints(sessionKey!),
    enabled: !!sessionKey && shouldConnectWS,
    staleTime: sessionMode === 'replay' ? Infinity : 0,
    gcTime: sessionMode === 'replay' ? Infinity : 0,
    retry: 3,
  })

  const {
    data: initialPits,
    isLoading: isLoadingPits,
  } = useQuery({
    queryKey: ['live', 'pits', sessionKey],
    queryFn: () => liveApi.getLivePits(sessionKey!),
    enabled: !!sessionKey && shouldConnectWS,
    staleTime: sessionMode === 'replay' ? Infinity : 0,
    gcTime: sessionMode === 'replay' ? Infinity : 0,
    retry: 3,
  })

  const {
    data: initialWeather,
    isLoading: isLoadingWeather,
  } = useQuery({
    queryKey: ['live', 'weather', sessionKey],
    queryFn: () => liveApi.getLiveWeather(sessionKey!),
    enabled: !!sessionKey && shouldConnectWS,
    staleTime: sessionMode === 'replay' ? Infinity : 0,
    gcTime: sessionMode === 'replay' ? Infinity : 0,
    retry: 3,
  })

  // Set initial data in store
  const updatePositions = useLiveRaceStore((s) => s.updatePositions)
  const updateIntervals = useLiveRaceStore((s) => s.updateIntervals)
  const addRaceControlMessage = useLiveRaceStore((s) => s.addRaceControlMessage)
  const updateStints = useLiveRaceStore((s) => s.updateStints)
  const addPitStop = useLiveRaceStore((s) => s.addPitStop)
  const updateWeather = useLiveRaceStore((s) => s.updateWeather)

  useEffect(() => {
    if (initialPositions) updatePositions(initialPositions)
  }, [initialPositions, updatePositions])

  useEffect(() => {
    if (initialIntervals) updateIntervals(initialIntervals)
  }, [initialIntervals, updateIntervals])

  useEffect(() => {
    if (initialRaceControl) {
      initialRaceControl.forEach(msg => addRaceControlMessage(msg))
    }
  }, [initialRaceControl, addRaceControlMessage])
  
  useEffect(() => {
    if (initialStints) updateStints(initialStints)
  }, [initialStints, updateStints])
  
  useEffect(() => {
    if (initialPits) {
      initialPits.forEach(p => addPitStop(p))
    }
  }, [initialPits, addPitStop])
  
  useEffect(() => {
    if (initialWeather) updateWeather(initialWeather)
  }, [initialWeather, updateWeather])

  return {
    // Session info
    sessionInfo: currentSession,
    sessionMode,
    isLoadingSession,
    sessionError,
    refetchSession,
    
    // WebSocket status
    wsStatus,
    wsRetryCount: retryCount,
    wsReconnect: reconnect,
    wsMaxRetries: maxRetries,
    
    // Initial data loading states
    isLoadingInitialData: isLoadingPositions || isLoadingIntervals || isLoadingRaceControl || isLoadingStints || isLoadingPits || isLoadingWeather,
    
    // Overall loading state
    isLoading: isLoadingSession || (shouldConnectWS && (isLoadingPositions || isLoadingIntervals || isLoadingRaceControl || isLoadingStints || isLoadingPits || isLoadingWeather)),
  }
}
