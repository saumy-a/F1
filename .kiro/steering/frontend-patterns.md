---
title: Frontend Patterns
inclusion: auto
---

# Frontend Patterns for F1 Dashboard

## WebSocket Hook with Exponential Backoff

```typescript
// src/hooks/useWebSocket.ts
import { useEffect, useRef, useState } from 'react'
import { useLiveRaceStore } from '../store/liveRaceStore'

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
    maxRetries = 5,
    initialRetryDelay = 1000,
    maxRetryDelay = 30000,
  } = options

  const [status, setStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected')
  const wsRef = useRef<WebSocket | null>(null)
  const retryCountRef = useRef(0)
  const retryTimeoutRef = useRef<NodeJS.Timeout>()

  const setPositions = useLiveRaceStore((s) => s.setPositions)
  const setIntervals = useLiveRaceStore((s) => s.setIntervals)
  const appendRCEvent = useLiveRaceStore((s) => s.appendRaceControlEvent)

  const calculateRetryDelay = (retryCount: number): number => {
    const delay = initialRetryDelay * Math.pow(2, retryCount)
    return Math.min(delay, maxRetryDelay)
  }

  const connect = () => {
    if (!sessionKey) return

    setStatus('connecting')
    const ws = new WebSocket(
      `${import.meta.env.VITE_WS_BASE_URL}/ws/live/${sessionKey}`
    )

    ws.onopen = () => {
      console.log('WebSocket connected for session', sessionKey)
      setStatus('connected')
      retryCountRef.current = 0 // Reset retry count on successful connection
    }

    ws.onmessage = (e) => {
      try {
        const { positions, intervals, race_control } = JSON.parse(e.data)
        if (positions) setPositions(positions)
        if (intervals) setIntervals(intervals)
        if (race_control) race_control.forEach(appendRCEvent)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onerror = (e) => {
      console.error('WebSocket error:', e)
      setStatus('error')
    }

    ws.onclose = (e) => {
      console.log('WebSocket closed for session', sessionKey, 'Code:', e.code)
      setStatus('disconnected')
      wsRef.current = null

      // Attempt reconnection with exponential backoff
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
        console.error('Max reconnection attempts reached')
        setStatus('error')
      }
    }

    wsRef.current = ws
  }

  useEffect(() => {
    if (!sessionKey) {
      setStatus('disconnected')
      return
    }

    connect()

    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [sessionKey])

  return { status }
}
```

## React Query Configuration

```typescript
// src/main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
      retry: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

## Zustand Store Patterns

```typescript
// src/store/liveRaceStore.ts
import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import type { Position, Interval, RaceControlEvent } from '../types/live'

interface LiveRaceStore {
  positions: Position[]
  intervals: Interval[]
  raceControlEvents: RaceControlEvent[]
  setPositions: (p: Position[]) => void
  setIntervals: (i: Interval[]) => void
  appendRaceControlEvent: (e: RaceControlEvent) => void
  clear: () => void
}

export const useLiveRaceStore = create<LiveRaceStore>()(
  devtools(
    (set) => ({
      positions: [],
      intervals: [],
      raceControlEvents: [],
      
      setPositions: (positions) => set({ positions }, false, 'setPositions'),
      
      setIntervals: (intervals) => set({ intervals }, false, 'setIntervals'),
      
      appendRaceControlEvent: (event) =>
        set(
          (state) => ({
            raceControlEvents: [event, ...state.raceControlEvents].slice(0, 200),
          }),
          false,
          'appendRaceControlEvent'
        ),
      
      clear: () =>
        set(
          { positions: [], intervals: [], raceControlEvents: [] },
          false,
          'clear'
        ),
    }),
    { name: 'LiveRaceStore' }
  )
)

// src/store/userPrefsStore.ts - with persistence
export const useUserPrefsStore = create<UserPrefsStore>()(
  devtools(
    persist(
      (set) => ({
        selectedYear: new Date().getFullYear().toString(),
        favouriteDrivers: [],
        theme: 'dark',
        
        setSelectedYear: (year) => set({ selectedYear: year }),
        toggleFavouriteDriver: (driverId) =>
          set((state) => ({
            favouriteDrivers: state.favouriteDrivers.includes(driverId)
              ? state.favouriteDrivers.filter((id) => id !== driverId)
              : [...state.favouriteDrivers, driverId],
          })),
        setTheme: (theme) => set({ theme }),
      }),
      { name: 'user-prefs' }
    ),
    { name: 'UserPrefsStore' }
  )
)
```

## Axios Client with Interceptors

```typescript
// src/api/client.ts
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add request ID for tracing
    config.headers['X-Request-ID'] = crypto.randomUUID()
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data)
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message)
    } else {
      // Something else happened
      console.error('Error:', error.message)
    }
    return Promise.reject(error)
  }
)
```

## Error Boundary

```typescript
// src/components/ErrorBoundary.tsx
import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-red-600 mb-4">
                Something went wrong
              </h1>
              <p className="text-gray-600 mb-4">
                {this.state.error?.message || 'An unexpected error occurred'}
              </p>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Reload Page
              </button>
            </div>
          </div>
        )
      )
    }

    return this.props.children
  }
}
```

## Code Splitting

```typescript
// src/App.tsx
import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/layout/Layout'
import { LoadingSpinner } from './components/shared/LoadingSpinner'

// Lazy load pages
const OverviewPage = lazy(() => import('./pages/OverviewPage'))
const DriverStandingsPage = lazy(() => import('./pages/DriverStandingsPage'))
const LiveTrackerPage = lazy(() => import('./pages/LiveTrackerPage'))

export function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={<LoadingSpinner />}>
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/standings/drivers" element={<DriverStandingsPage />} />
            <Route path="/live" element={<LiveTrackerPage />} />
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  )
}
```
