import { useDriverStandings } from '../hooks/useStandings'
import { useUserPrefsStore } from '../store/userPrefsStore'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import { LineChart } from '../components/charts/LineChart'
import { CHART_COLORS } from '../utils/constants'

export default function ChampionshipPage() {
  const selectedYear = useUserPrefsStore((state) => state.selectedYear)
  const { data: standings, isLoading, error, refetch } = useDriverStandings(selectedYear)

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Failed to load championship data" onRetry={refetch} />

  // For now, show current standings as a simple progression
  // In a full implementation, this would fetch standings for each round
  const topDrivers = standings?.slice(0, 8) || []
  
  const chartData = topDrivers.map((driver, index) => ({
    x: ['Current'],
    y: [parseFloat(driver.points)],
    name: `${driver.Driver.givenName} ${driver.Driver.familyName}`,
    mode: 'lines+markers' as const,
    line: {
      color: CHART_COLORS[index % CHART_COLORS.length],
      width: 2,
    },
    marker: {
      size: 8,
    },
  }))

  return (
    <div className="p-6">
      <h1 className="text-3xl font-display text-f1-white tracking-wider uppercase mb-6">Championship Progression - {selectedYear}</h1>
      
      <div className="mb-4 text-gray-400">
        Championship points progression throughout the season
      </div>

      {chartData.length > 0 ? (
        <LineChart
          data={chartData}
          title="Driver Championship Points"
          xAxisTitle="Race"
          yAxisTitle="Points"
          height={600}
        />
      ) : (
        <div className="text-center py-8 text-gray-400">
          No championship data available
        </div>
      )}

      <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-sm text-yellow-800">
          <strong>Note:</strong> Full round-by-round progression requires additional API endpoints. 
          Currently showing final standings.
        </p>
      </div>
    </div>
  )
}
