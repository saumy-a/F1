import { useState, useEffect } from 'react'
import { useRaceSchedule, useLapTimes } from '../hooks/useRaces'
import { useUserPrefsStore } from '../store/userPrefsStore'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import { ScatterChart } from '../components/charts/ScatterChart'
import { CHART_COLORS } from '../utils/constants'

export default function LapTimesPage() {
  const selectedYear = useUserPrefsStore((state) => state.selectedYear)
  const { data: races } = useRaceSchedule(selectedYear)
  const [selectedRound, setSelectedRound] = useState<string>('1')
  
  // Update selectedRound when races load
  useEffect(() => {
    if (races && races.length > 0 && !races.find(r => r.round === selectedRound)) {
      setSelectedRound(races[0].round)
    }
  }, [races, selectedRound])
  
  const { data: lapTimes, isLoading, error, refetch } = useLapTimes(
    selectedYear,
    parseInt(selectedRound)
  )

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Failed to load lap times" onRetry={refetch} />

  // Group lap times by driver
  const driverLapTimes = lapTimes?.reduce((acc, lap) => {
    if (!acc[lap.driverId]) {
      acc[lap.driverId] = []
    }
    acc[lap.driverId].push(lap)
    return acc
  }, {} as Record<string, typeof lapTimes>)

  // Convert lap times to seconds for plotting
  const timeToSeconds = (timeStr: string): number => {
    const parts = timeStr.split(':')
    if (parts.length === 2) {
      const [minutes, seconds] = parts
      return parseFloat(minutes) * 60 + parseFloat(seconds)
    }
    return parseFloat(timeStr)
  }

  const chartData = Object.entries(driverLapTimes || {}).map(([driverId, laps], index) => ({
    x: laps.map(lap => parseInt(lap.lap)),
    y: laps.map(lap => timeToSeconds(lap.time)),
    text: laps.map(lap => `${driverId} - Lap ${lap.lap}: ${lap.time}`),
    name: driverId,
    mode: 'lines+markers' as const,
    marker: {
      color: CHART_COLORS[index % CHART_COLORS.length],
      size: 4,
    },
  }))

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Lap Times Analysis - {selectedYear}</h1>
      
      <div className="mb-6">
        <label htmlFor="round-select" className="block text-sm font-medium text-gray-700 mb-2">
          Select Race
        </label>
        <select
          id="round-select"
          value={selectedRound}
          onChange={(e) => setSelectedRound(e.target.value)}
          className="block w-full max-w-md px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-red-600 focus:border-red-600"
        >
          {races?.map((race) => (
            <option key={race.round} value={race.round}>
              Round {race.round}: {race.raceName}
            </option>
          ))}
        </select>
      </div>

      {chartData.length > 0 && (
        <ScatterChart
          data={chartData}
          title="Lap Times Throughout Race"
          xAxisTitle="Lap Number"
          yAxisTitle="Lap Time (seconds)"
          height={600}
        />
      )}

      {chartData.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No lap time data available for this race
        </div>
      )}
    </div>
  )
}
