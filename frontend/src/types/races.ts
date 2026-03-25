import type { DriverInfo, ConstructorInfo } from './common'

export interface Location {
  lat: string
  long: string
  locality: string
  country: string
}

export interface Circuit {
  circuitId: string
  circuitName: string
  Location: Location
  url?: string
}

export interface Race {
  season: string
  round: string
  raceName: string
  Circuit: Circuit
  date: string
  time?: string
  url?: string
}

export interface FastestLap {
  rank: string
  lap: string
  Time: {
    time: string
  }
  AverageSpeed: {
    units: string
    speed: string
  }
}

export interface RaceResultEntry {
  position: string
  points: string
  Driver: DriverInfo
  Constructor: ConstructorInfo
  grid: string
  laps: string
  status: string
  Time?: {
    millis: string
    time: string
  }
  FastestLap?: FastestLap
}

export interface RaceResult {
  season: string
  round: string
  raceName: string
  Circuit: Circuit
  date: string
  Results: RaceResultEntry[]
}

export interface QualifyingResultEntry {
  position: string
  Driver: DriverInfo
  Constructor: ConstructorInfo
  Q1?: string
  Q2?: string
  Q3?: string
}

export interface QualifyingResult {
  season: string
  round: string
  raceName: string
  Circuit: Circuit
  date: string
  QualifyingResults: QualifyingResultEntry[]
}

export interface LapTime {
  driverId: string
  lap: string
  position: string
  time: string
}
