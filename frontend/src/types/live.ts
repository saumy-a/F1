export type SessionMode = 'live' | 'upcoming' | 'replay'

export interface SessionInfo {
  session_key: string
  session_name: string
  session_type: string
  date_start: string
  date_end: string
  gmt_offset: string
  location: string
  country_name: string
  circuit_short_name: string
  mode: SessionMode
}

export interface Position {
  driver_number: number
  position: number
  date: string
}

export interface Interval {
  driver_number: number
  gap_to_leader: number | string | null
  interval: number | string | null
  date: string
}

export interface Stint {
  driver_number: number
  stint_number: number
  compound: 'SOFT' | 'MEDIUM' | 'HARD' | 'INTERMEDIATE' | 'WET'
  tyre_age_at_start: number
  lap_start: number
  lap_end: number | null
}

export interface PitStop {
  driver_number: number
  lap_number: number
  stop_duration: number | null
  lane_duration: number
  date: string
}

export interface Weather {
  air_temperature: number
  track_temperature: number
  humidity: number
  pressure: number
  rainfall: number
  wind_direction: number
  wind_speed: number
  date: string
}

export interface RaceControlMessage {
  category: string
  message: string
  date: string
  lap_number: number | null
  driver_number: number | null
  flag: 'YELLOW' | 'RED' | 'GREEN' | 'BLUE' | 'CHEQUERED' | null
}

export interface TeamRadio {
  driver_number: number
  date: string
  recording_url: string
  duration: number
}

export interface Driver {
  driver_number: number
  broadcast_name: string
  full_name: string
  name_acronym: string
  team_name: string
  team_colour: string
  headshot_url: string | null
}

export interface WebSocketMessage {
  type: 'update' | 'ping' | 'error'
  timestamp: string
  positions?: Position[]
  intervals?: Interval[]
  race_control?: RaceControlMessage[]
  message?: string
  code?: number
}
