export interface DriverInfo {
  driverId: string
  givenName: string
  familyName: string
  nationality?: string
  permanentNumber?: string
  code?: string
  dateOfBirth?: string
  url?: string
}

export interface ConstructorInfo {
  constructorId: string
  name: string
  nationality?: string
  url?: string
}
