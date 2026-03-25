import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { DriverStanding, ConstructorStanding } from '../types/standings'

export function useDriverStandings(year: string, round?: number) {
  return useQuery({
    queryKey: ['driver-standings', year, round],
    queryFn: async () => {
      const params = round ? { round } : {}
      const response = await apiClient.get<DriverStanding[]>(
        `/api/standings/drivers/${year}`,
        { params }
      )
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes for historical data
    enabled: !!year,
  })
}

export function useConstructorStandings(year: string, round?: number) {
  return useQuery({
    queryKey: ['constructor-standings', year, round],
    queryFn: async () => {
      const params = round ? { round } : {}
      const response = await apiClient.get<ConstructorStanding[]>(
        `/api/standings/constructors/${year}`,
        { params }
      )
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes for historical data
    enabled: !!year,
  })
}
