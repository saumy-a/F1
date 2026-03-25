import { useEffect, useRef, useState } from 'react'
import { useLiveRaceStore } from '../store/liveRaceStore'
import type { WebSocketMessage } from '../types/live'

interface UseWebSocketOptions {
  maxRetries?: number
  initialRetryDelay?: number
  maxRetryDelay?: number
}

export const useWebSocket = (
  sessionKey: string | null,
  options: UseWebSocketOptions = {}
) => {
  const {
    maxRetries = 10, // Stop reconnecting after 10 failed attempts
    initialRetryDelay = 1000, // Start with 1 second
    maxRetryDelay = 30000, // Max 30 seconds
  } = options

  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const wsRef = useRef<WebSocket | null>(null)
  const retryCountRef = useRef(0)
  const retryTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)
  const pingTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined)

  // Store actions
  const updatePositions = useLiveRaceStore((s) => s.updatePositions)
  const updateIntervals = useLiveRaceStore((s) => s.updateIntervals)
  const addRaceControlMessage = useLiveRaceStore((s) => s.addRaceControlMessage)
  const setConnectionStatus = useLiveRaceStore((s) => s.setConnectionStatus)

  // Calculate exponential backoff delay: 1s → 2s → 4s → 8s → 16s → 30s max
  const calculateRetryDelay = (retryCount: number): number => {
    const delay = initialRetryDelay * Math.pow(2, retryCount)
    return Math.min(delay, maxRetryDelay)
  }

  const resetPingTimeout = () => {
    if (pingTimeoutRef.current) {
      clearTimeout(pingTimeoutRef.current)
    }
    // Expect ping every 30s, timeout after 45s
    pingTimeoutRef.current = setTimeout(() => {
      console.warn('WebSocket ping timeout - closing connection')
      wsRef.current?.close()
    }, 45000)
  }

  const connect = () => {
    if (!sessionKey) return

    setStatus('connecting')
    setConnectionStatus(false)

    const wsUrl = `${import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'}/ws/live/${sessionKey}`
    console.log('Connecting to WebSocket:', wsUrl)
    
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected for session', sessionKey)
      setStatus('connected')
      setConnectionStatus(true)
      retryCountRef.current = 0 // Reset retry count on successful connection
      resetPingTimeout()
    }

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data)
        
        // Validate message structure before updating state
        if (!data.type || !data.timestamp) {
          console.warn('Invalid WebSocket message structure:', data)
          return
        }

        // Handle ping/pong for heartbeat
        if (data.type === 'ping') {
          resetPingTimeout()
          // Respond to ping with pong message
          ws.send(JSON.stringify({ type: 'pong' }))
          return
        }

        // Handle error messages
        if (data.type === 'error') {
          console.error('WebSocket server error:', data.message, 'Code:', data.code)
          return
        }

        // Handle data updates
        if (data.type === 'update') {
          if (data.positions && Array.isArray(data.positions)) {
            updatePositions(data.positions)
          }
          if (data.intervals && Array.isArray(data.intervals)) {
            updateIntervals(data.intervals)
          }
          if (data.race_control && Array.isArray(data.race_control)) {
            data.race_control.forEach(msg => addRaceControlMessage(msg))
          }
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onerror = (event) => {
      console.error('WebSocket error:', event)
      setStatus('error')
      setConnectionStatus(false)
    }

    ws.onclose = (event) => {
      console.log('WebSocket closed for session', sessionKey, 'Code:', event.code, 'Reason:', event.reason)
      setStatus('disconnected')
      setConnectionStatus(false)
      wsRef.current = null

      // Clear ping timeout
      if (pingTimeoutRef.current) {
        clearTimeout(pingTimeoutRef.current)
      }

      // Attempt reconnection with exponential backoff (stop after 10 failed attempts)
      if (retryCountRef.current < maxRetries) {
        const delay = calculateRetryDelay(retryCountRef.current)
        console.log(
          `Reconnecting in ${delay}ms (attempt ${retryCountRef.current + 1}/${maxRetries})`
        )
        
        retryTimeoutRef.current = setTimeout(() => {
          retryCountRef.current++
          connect()
        }, delay)
      } else {
        console.error(`Max reconnection attempts reached (${maxRetries})`)
        setStatus('error')
        setConnectionStatus(false)
      }
    }

    wsRef.current = ws
  }

  useEffect(() => {
    // Close connection when enabled=false or component unmounts
    if (!sessionKey) {
      setStatus('disconnected')
      setConnectionStatus(false)
      return
    }

    // Connect when enabled=true
    connect()

    return () => {
      // Cleanup on unmount
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
      if (pingTimeoutRef.current) {
        clearTimeout(pingTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [sessionKey])

  return { status }
}

