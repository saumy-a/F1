import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { Race, RaceResult, QualifyingResult, LapTime } from '../types/races'

export function useRaceSchedule(year: string) {
  return useQuery({
    queryKey: ['race-schedule', year],
    queryFn: async () => {
      const response = await apiClient.get<Race[]>(
        `/api/races/${year}`
      )
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes for historical data
    enabled: !!year,
  })
}

export function useRaceResults(year: string, round: number) {
  return useQuery({
    queryKey: ['race-results', year, round],
    queryFn: async () => {
      const response = await apiClient.get<RaceResult>(
        `/api/races/${year}/${round}/results`
      )
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes for historical data
    enabled: !!year && !!round,
  })
}

export function useQualifyingResults(year: string, round: number) {
  return useQuery({
    queryKey: ['qualifying-results', year, round],
    queryFn: async () => {
      const response = await apiClient.get<QualifyingResult>(
        `/api/races/${year}/${round}/qualifying`
      )
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes for historical data
    enabled: !!year && !!round,
  })
}

export function useLapTimes(year: string, round: number) {
  return useQuery({
    queryKey: ['lap-times', year, round],
    queryFn: async () => {
      const response = await apiClient.get<LapTime[]>(
        `/api/races/${year}/${round}/laps`
      )
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes for historical data
    enabled: !!year && !!round,
  })
}
