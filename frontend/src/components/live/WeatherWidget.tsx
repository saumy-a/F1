import { useQuery } from '@tanstack/react-query'
import { liveApi } from '../../api/live'
import { useSessionStore } from '../../store/sessionStore'

export const WeatherWidget = () => {
  const currentSession = useSessionStore((s) => s.currentSession)
  const sessionMode = useSessionStore((s) => s.sessionMode)

  const { data: weather, isLoading } = useQuery({
    queryKey: ['live', 'weather', currentSession?.session_key],
    queryFn: () => liveApi.getLiveWeather(currentSession!.session_key),
    enabled: !!currentSession?.session_key && (sessionMode === 'live' || sessionMode === 'replay'),
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  if (isLoading) {
    return (
      <div className="f1-panel p-6">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase mb-4">Weather</h2>
        <div className="text-center text-gray-400 py-4">
          Loading weather data...
        </div>
      </div>
    )
  }

  if (!weather) {
    return (
      <div className="f1-panel p-6">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase mb-4">Weather</h2>
        <div className="text-center text-gray-400 py-4">
          No weather data available
        </div>
      </div>
    )
  }

  const getRainfallIcon = (rainfall: number) => {
    if (rainfall === 0) return '☀️'
    if (rainfall < 5) return '🌦️'
    return '🌧️'
  }

  const getWindDirection = (degrees: number) => {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    const index = Math.round(degrees / 45) % 8
    return directions[index]
  }

  return (
    <div className="f1-panel">
      <div className="p-4 border-b border-f1-border flex justify-between items-center">
        <h2 className="text-xl font-display text-f1-white tracking-wider uppercase">Weather</h2>
        <span className="text-2xl">{getRainfallIcon(weather.rainfall)}</span>
      </div>
      
      <div className="p-4 grid grid-cols-2 gap-4">
        {/* Air Temperature */}
        <div className="bg-f1-red/10 border-f1-red/20 rounded-lg p-3">
          <div className="text-xs text-f1-red font-medium mb-1">Air Temp</div>
          <div className="text-2xl font-display text-f1-white tracking-wider uppercase text-f1-red f1-text-glow">
            {weather.air_temperature.toFixed(1)}°C
          </div>
        </div>

        {/* Track Temperature */}
        <div className="bg-orange-50 rounded-lg p-3">
          <div className="text-xs text-orange-600 font-medium mb-1">Track Temp</div>
          <div className="text-2xl font-display text-f1-white tracking-wider uppercase text-orange-900">
            {weather.track_temperature.toFixed(1)}°C
          </div>
        </div>

        {/* Humidity */}
        <div className="bg-cyan-50 rounded-lg p-3">
          <div className="text-xs text-cyan-600 font-medium mb-1">Humidity</div>
          <div className="text-2xl font-display text-f1-white tracking-wider uppercase text-cyan-900">
            {weather.humidity}%
          </div>
        </div>

        {/* Pressure */}
        <div className="bg-purple-50 rounded-lg p-3">
          <div className="text-xs text-purple-600 font-medium mb-1">Pressure</div>
          <div className="text-2xl font-display text-f1-white tracking-wider uppercase text-purple-900">
            {weather.pressure.toFixed(0)} hPa
          </div>
        </div>

        {/* Wind */}
        <div className="bg-green-50 rounded-lg p-3 col-span-2">
          <div className="text-xs text-green-600 font-medium mb-1">Wind</div>
          <div className="flex items-center justify-between">
            <div className="text-xl font-display text-f1-white tracking-wider uppercase text-green-900">
              {weather.wind_speed.toFixed(1)} m/s
            </div>
            <div className="text-lg font-medium text-green-700">
              {getWindDirection(weather.wind_direction)} ({weather.wind_direction}°)
            </div>
          </div>
        </div>

        {/* Rainfall */}
        {weather.rainfall > 0 && (
          <div className="bg-blue-100 rounded-lg p-3 col-span-2 border-2 border-blue-300">
            <div className="text-xs text-f1-red/80 font-medium mb-1">⚠️ Rainfall Detected</div>
            <div className="text-xl font-display text-f1-white tracking-wider uppercase text-f1-red f1-text-glow">
              {weather.rainfall > 0 ? 'Wet Track Conditions' : 'Dry Track'}
            </div>
          </div>
        )}
      </div>

      {weather.date && (
        <div className="px-4 pb-3 text-xs text-gray-400 text-center">
          Updated: {new Date(weather.date).toLocaleTimeString()}
        </div>
      )}
    </div>
  )
}
