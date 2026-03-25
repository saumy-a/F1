import type { DriverInfo, ConstructorInfo } from './common'

export interface DriverStanding {
  position: string
  points: string
  wins: string
  Driver: DriverInfo
  Constructors: ConstructorInfo[]
}

export interface ConstructorStanding {
  position: string
  points: string
  wins: string
  Constructor: ConstructorInfo
}
