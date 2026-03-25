export interface PerformanceTrend {
  data: any[]
  layout: Record<string, any>
}

export interface ConsistencyScore {
  score: number
  std_dev: number
  mean_position: number
}

export interface DNFRate {
  dnf_count: number
  total_races: number
  dnf_rate: number
}

export interface FormIndicator {
  avg_position: number
  total_points: number
  trend_direction: 'improving' | 'declining' | 'stable'
  trend_slope: number
  races_analyzed: number
}

export interface DriverComparison {
  drivers: string[]
  metrics: Record<string, number[]>
  chart_data: Record<string, any>
}

export interface ChampionshipProjection {
  projected_winner: string
  projected_points: Record<string, number>
  confidence: number
}

export interface CircuitPerformance {
  circuit_id: string
  circuit_name: string
  average_position: number
  best_finish: number
  podiums: number
  wins: number
}

export interface TeamReliability {
  constructor_id: string
  dnf_rate: number
  finish_rate: number
  average_points: number
}
