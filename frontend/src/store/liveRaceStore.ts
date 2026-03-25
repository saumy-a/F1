import { create } from 'zustand'
import type { Position, Interval, Stint, PitStop, Weather, RaceControlMessage, Driver, SessionInfo } from '../types/live'

interface LiveRaceState {
  // Session metadata
  sessionInfo: SessionInfo | null
  drivers: Driver[]
  
  // Live data
  positions: Position[]
  intervals: Interval[]
  intervalHistory: { lap: number; driver_number: number; gap: number | null }[]
  stints: Stint[]
  pitStops: PitStop[]
  weather: Weather | null
  raceControl: RaceControlMessage[]
  
  // WebSocket connection state
  isConnected: boolean
  lastUpdate: string | null
  
  // Actions
  setSessionInfo: (info: SessionInfo) => void
  setDrivers: (drivers: Driver[]) => void
  updatePositions: (positions: Position[]) => void
  updateIntervals: (intervals: Interval[]) => void
  appendIntervalHistory: (lap: number, driver_number: number, gap: number | null) => void
  updateStints: (stints: Stint[]) => void
  addPitStop: (pitStop: PitStop) => void
  updateWeather: (weather: Weather) => void
  addRaceControlMessage: (message: RaceControlMessage) => void
  setConnectionStatus: (connected: boolean) => void
  clearLiveData: () => void
}

export const useLiveRaceStore = create<LiveRaceState>((set) => ({
  sessionInfo: null,
  drivers: [],
  positions: [],
  intervals: [],
  intervalHistory: [],
  stints: [],
  pitStops: [],
  weather: null,
  raceControl: [],
  isConnected: false,
  lastUpdate: null,
  
  setSessionInfo: (info) => set({ sessionInfo: info }),
  setDrivers: (drivers) => set({ drivers }),
  
  updatePositions: (positions) => set({ 
    positions,
    lastUpdate: new Date().toISOString()
  }),
  
  updateIntervals: (intervals) => set({ 
    intervals,
    lastUpdate: new Date().toISOString()
  }),
  
  appendIntervalHistory: (lap, driver_number, gap) => set((state) => ({
    intervalHistory: [...state.intervalHistory, { lap, driver_number, gap }]
  })),
  
  updateStints: (stints) => set({ stints }),
  
  addPitStop: (pitStop) => set((state) => ({
    pitStops: [pitStop, ...state.pitStops]
  })),
  
  updateWeather: (weather) => set({ weather }),
  
  addRaceControlMessage: (message) => set((state) => ({
    raceControl: [message, ...state.raceControl]
  })),
  
  setConnectionStatus: (connected) => set({ isConnected: connected }),
  
  clearLiveData: () => set({
    positions: [],
    intervals: [],
    intervalHistory: [],
    stints: [],
    pitStops: [],
    weather: null,
    raceControl: [],
    isConnected: false,
    lastUpdate: null
  })
}))
