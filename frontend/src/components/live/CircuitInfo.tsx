import type { SessionInfo } from '../../types/live'
import { circuitDetailsMap } from '../../utils/circuitData'

interface CircuitInfoProps {
  sessionInfo: SessionInfo
}

export function CircuitInfo({ sessionInfo }: CircuitInfoProps) {
  // Extract circuit information from session info
  const circuitName = sessionInfo.circuit_short_name
  const location = sessionInfo.location
  const country = sessionInfo.country_name
  
  const details = circuitDetailsMap[circuitName]
  
  const circuitLength = details?.length || 'N/A'
  const numberOfLaps = details?.laps || 'N/A'
  const raceDistance = details?.distance || 'N/A'
  const lapRecord = details?.lapRecord || 'Lap record data not available'
  const drsZones = details?.drsZones || 'N/A'
  const circuitImage = details?.imageUrl || null
  
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Circuit Information</h3>
      
      <div className="space-y-4">
        {/* Circuit Name */}
        <div>
          <h4 className="text-2xl font-display text-f1-white tracking-wider uppercase text-f1-white">{circuitName}</h4>
          <p className="text-gray-400">{location}, {country}</p>
        </div>
        
        {/* Circuit Image */}
        {circuitImage ? (
          <div className="w-full bg-[#292a2c]/40 rounded-lg overflow-hidden flex items-center justify-center p-4">
            <img src={circuitImage} alt={`${circuitName} layout`} className="max-w-full max-h-48 object-contain opacity-80" />
          </div>
        ) : (
          <div className="w-full h-48 bg-[#292a2c]/40 rounded-lg flex items-center justify-center">
            <div className="text-center text-gray-400">
              <svg 
                className="w-16 h-16 mx-auto mb-2 opacity-50" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" 
                />
              </svg>
              <p className="text-sm">Circuit map not available</p>
            </div>
          </div>
        )}
        
        {/* Circuit Details Grid */}
        <div className="grid grid-cols-2 gap-4">
          <CircuitDetail 
            label="Circuit Length" 
            value={circuitLength}
            unit="km"
          />
          <CircuitDetail 
            label="Number of Laps" 
            value={numberOfLaps}
          />
          <CircuitDetail 
            label="Race Distance" 
            value={raceDistance}
            unit="km"
          />
          <CircuitDetail 
            label="DRS Zones" 
            value={drsZones}
          />
        </div>
        
        {/* Lap Record */}
        <div className="border-t border-[#343537]/30 pt-4">
          <h5 className="text-sm font-semibold text-gray-300 mb-2">Lap Record</h5>
          <div className="bg-[#292a2c]/40 rounded-lg p-3">
            <p className="text-f1-white text-sm">{lapRecord}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

interface CircuitDetailProps {
  label: string
  value: string
  unit?: string
}

function CircuitDetail({ label, value, unit }: CircuitDetailProps) {
  return (
    <div className="bg-[#292a2c]/40 rounded-lg p-3">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className="text-lg font-semibold text-f1-white">
        {value}
        {unit && value !== 'N/A' && <span className="text-sm text-gray-400 ml-1">{unit}</span>}
      </p>
    </div>
  )
}
