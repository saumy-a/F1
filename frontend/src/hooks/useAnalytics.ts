import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type {
  PerformanceTrend,
  ConsistencyScore,
  FormIndicator,
  DNFRate,
  DriverComparison,
  CircuitPerformance,
  ChampionshipProjection,
} from '../types/analytics'

export function usePerformanceTrends(driverId: string, year: string) {
  return useQuery({
    queryKey: ['performance-trends', driverId, year],
    queryFn: async () => {
      const response = await apiClient.get<PerformanceTrend>(
        `/api/analytics/trends/${driverId}/${year}`
      )
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes for analytics
    enabled: !!driverId && !!year,
  })
}

export function useConsistencyScore(driverId: string, year: string) {
  return useQuery({
    queryKey: ['consistency-score', driverId, year],
    queryFn: async () => {
      const response = await apiClient.get<ConsistencyScore>(
        `/api/analytics/consistency/${driverId}/${year}`
      )
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes for analytics
    enabled: !!driverId && !!year,
  })
}

export function useFormIndicator(driverId: string, year: string, lastN: number = 5) {
  return useQuery({
    queryKey: ['form-indicator', driverId, year, lastN],
    queryFn: async () => {
      const response = await apiClient.get<FormIndicator>(
        `/api/analytics/form/${driverId}/${year}`,
        { params: { last_n: lastN } }
      )
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes for analytics
    enabled: !!driverId && !!year,
  })
}

export function useDNFRate(driverId: string, year: string) {
  return useQuery({
    queryKey: ['dnf-rate', driverId, year],
    queryFn: async () => {
      const response = await apiClient.get<DNFRate>(
        `/api/analytics/dnf/${driverId}/${year}`
      )
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes for analytics
    enabled: !!driverId && !!year,
  })
}

export function useDriverComparison(driverIds: string[], year: string) {
  return useQuery({
    queryKey: ['driver-comparison', driverIds, year],
    queryFn: async () => {
      const response = await apiClient.post<DriverComparison>(
        '/api/analytics/compare',
        { driver_ids: driverIds, year }
      )
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes for analytics
    enabled: driverIds.length >= 2 && !!year,
  })
}

export function useCircuitPerformance(circuitId: string, year: string) {
  return useQuery({
    queryKey: ['circuit-performance', circuitId, year],
    queryFn: async () => {
      const response = await apiClient.get<CircuitPerformance>(
        `/api/analytics/circuit/${circuitId}`,
        { params: { year } }
      )
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes for analytics
    enabled: !!circuitId && !!year,
  })
}

export function useChampionshipProjection(year: string) {
  return useQuery({
    queryKey: ['championship-projection', year],
    queryFn: async () => {
      const response = await apiClient.get<ChampionshipProjection>(
        `/api/analytics/projection/${year}`
      )
      return response.data
    },
    staleTime: 10 * 60 * 1000, // 10 minutes for analytics
    enabled: !!year,
  })
}
