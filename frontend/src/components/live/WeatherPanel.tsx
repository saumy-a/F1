import React from 'react'
import { useLiveRaceStore } from '../../store/liveRaceStore'

export const WeatherPanel = React.memo(function WeatherPanel() {
  const weather = useLiveRaceStore((state) => state.weather)
  
  // Helper function to get weather icon based on rainfall
  const getWeatherIcon = (rainfall: number): string => {
    if (rainfall === 0) return '☀️'
    if (rainfall < 5) return '🌦️'
    return '🌧️'
  }
  
  // Helper function to convert wind direction degrees to compass direction
  const getWindDirection = (degrees: number): string => {
    const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    const index = Math.round(degrees / 45) % 8
    return directions[index]
  }
  
  return (
    <div className="f1-panel">
      <div className="bg-gray-800 text-white px-4 py-3 font-semibold flex justify-between items-center">
        <span>Weather</span>
        {weather && (
          <span className="text-2xl">{getWeatherIcon(weather.rainfall)}</span>
        )}
      </div>
      
      {!weather ? (
        <div className="px-4 py-8 text-center text-gray-400">
          No weather data available
        </div>
      ) : (
        <>
          <div className="p-4 grid grid-cols-2 gap-4">
            {/* Track Temperature */}
            <div className="bg-orange-50 rounded-lg p-3">
              <div className="text-xs text-orange-600 font-medium mb-1">Track Temp</div>
              <div className="text-2xl font-display text-f1-white tracking-wider uppercase text-orange-900">
                {weather.track_temperature.toFixed(1)}°C
              </div>
            </div>
            
            {/* Air Temperature */}
            <div className="bg-f1-red/10 border-f1-red/20 rounded-lg p-3">
              <div className="text-xs text-f1-red font-medium mb-1">Air Temp</div>
              <div className="text-2xl font-display text-f1-white tracking-wider uppercase text-f1-red f1-text-glow">
                {weather.air_temperature.toFixed(1)}°C
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
            
            {/* Rainfall */}
            <div 
              className={`rounded-lg p-3 col-span-2 ${
                weather.rainfall === 1 
                  ? 'bg-blue-100 border-2 border-blue-300' 
                  : 'bg-[#292a2c]/40'
              }`}
            >
              <div className={`text-xs font-medium mb-1 ${
                weather.rainfall === 1 ? 'text-f1-red/80' : 'text-gray-400'
              }`}>
                {weather.rainfall === 1 ? '⚠️ Rainfall' : 'Rainfall'}
              </div>
              <div className={`text-xl font-display text-f1-white tracking-wider uppercase ${
                weather.rainfall === 1 ? 'text-f1-red f1-text-glow' : 'text-f1-white'
              }`}>
                {weather.rainfall === 1 ? 'Wet Track Conditions' : 'Dry Track'}
              </div>
            </div>
            
            {/* Wind Direction */}
            <div className="bg-green-50 rounded-lg p-3">
              <div className="text-xs text-green-600 font-medium mb-1">Wind Direction</div>
              <div className="text-xl font-display text-f1-white tracking-wider uppercase text-green-900">
                {getWindDirection(weather.wind_direction)} ({weather.wind_direction}°)
              </div>
            </div>
            
            {/* Wind Speed */}
            <div className="bg-green-50 rounded-lg p-3">
              <div className="text-xs text-green-600 font-medium mb-1">Wind Speed</div>
              <div className="text-xl font-display text-f1-white tracking-wider uppercase text-green-900">
                {weather.wind_speed.toFixed(1)} km/h
              </div>
            </div>
          </div>
          
          {weather.date && (
            <div className="px-4 pb-3 text-xs text-gray-400 text-center">
              Updated: {new Date(weather.date).toLocaleTimeString()}
            </div>
          )}
        </>
      )}
    </div>
  )
})
