import { apiClient } from './client'
import type { SessionInfo, Driver, Position, Interval, Weather, Stint, PitStop, RaceControlMessage } from '../types/live'

export const liveApi = {
  // Get current session info
  getCurrentSession: async (): Promise<SessionInfo> => {
    const response = await apiClient.get<SessionInfo>('/api/live/session')
    return response.data
  },

  // Get sessions by year
  getSessionsByYear: async (year: number): Promise<SessionInfo[]> => {
    const response = await apiClient.get<SessionInfo[]>(`/api/live/sessions?year=${year}`)
    return response.data
  },

  // Get live positions (path parameter)
  getLivePositions: async (sessionKey: string): Promise<Position[]> => {
    const response = await apiClient.get<Position[]>(`/api/live/positions/${sessionKey}`)
    return response.data
  },

  // Get live intervals (path parameter)
  getLiveIntervals: async (sessionKey: string): Promise<Interval[]> => {
    const response = await apiClient.get<Interval[]>(`/api/live/intervals/${sessionKey}`)
    return response.data
  },

  // Get live stints (path parameter)
  getLiveStints: async (sessionKey: string): Promise<Stint[]> => {
    const response = await apiClient.get<Stint[]>(`/api/live/stints/${sessionKey}`)
    return response.data
  },

  // Get pit stops (path parameter)
  getLivePits: async (sessionKey: string): Promise<PitStop[]> => {
    const response = await apiClient.get<PitStop[]>(`/api/live/pits/${sessionKey}`)
    return response.data
  },

  // Get weather (path parameter)
  getLiveWeather: async (sessionKey: string): Promise<Weather> => {
    const response = await apiClient.get<Weather>(`/api/live/weather/${sessionKey}`)
    return response.data
  },

  // Get race control messages (path parameter)
  getRaceControl: async (sessionKey: string): Promise<RaceControlMessage[]> => {
    const response = await apiClient.get<RaceControlMessage[]>(`/api/live/race-control/${sessionKey}`)
    return response.data
  },

  // Get team radio (path parameter)
  getTeamRadio: async (sessionKey: string) => {
    const response = await apiClient.get(`/api/live/radio/${sessionKey}`)
    return response.data
  },

  // Get starting grid (path parameter)
  getStartingGrid: async (sessionKey: string): Promise<Driver[]> => {
    const response = await apiClient.get<Driver[]>(`/api/live/grid/${sessionKey}`)
    return response.data
  },
}
