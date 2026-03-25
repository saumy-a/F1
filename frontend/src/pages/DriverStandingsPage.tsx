import { useDriverStandings } from '../hooks/useStandings'
import { useUserPrefsStore } from '../store/userPrefsStore'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import { DataTable } from '../components/shared/DataTable'
import { HorizontalBarChart } from '../components/charts/HorizontalBarChart'
import { CHART_COLORS } from '../utils/constants'

export default function DriverStandingsPage() {
  const selectedYear = useUserPrefsStore((state) => state.selectedYear)
  const { data: standings, isLoading, error, refetch } = useDriverStandings(selectedYear)

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Failed to load driver standings" onRetry={refetch} />
  if (!standings || standings.length === 0) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-6">Driver Standings - {selectedYear}</h1>
        <div className="text-center py-12 text-gray-500">
          No driver standings data available for {selectedYear}
        </div>
      </div>
    )
  }

  const columns = [
    { header: 'Position', accessor: 'position' as const },
    { 
      header: 'Driver', 
      accessor: (row: any) => {
        const driver = row.Driver
        if (!driver) return '-'
        return `${driver.givenName || ''} ${driver.familyName || ''}`.trim() || '-'
      }
    },
    { 
      header: 'Nationality', 
      accessor: (row: any) => row.Driver?.nationality || '-' 
    },
    { 
      header: 'Team', 
      accessor: (row: any) => {
        const constructors = row.Constructors
        if (!constructors || !Array.isArray(constructors) || constructors.length === 0) return '-'
        return constructors[0]?.name || '-'
      }
    },
    { header: 'Points', accessor: 'points' as const, className: 'font-semibold' },
    { header: 'Wins', accessor: 'wins' as const },
  ]

  const chartData = {
    x: standings.map(s => parseFloat(s.points)),
    y: standings.map(s => `${s.Driver.givenName} ${s.Driver.familyName}`),
    text: standings.map(s => s.points),
    marker: {
      color: CHART_COLORS,
    },
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Driver Standings - {selectedYear}</h1>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Standings Table</h2>
        <DataTable data={standings} columns={columns} />
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Points Distribution</h2>
        <HorizontalBarChart
          data={chartData}
          title="Driver Championship Points"
          xAxisTitle="Points"
          yAxisTitle="Driver"
          height={Math.max(400, standings.length * 30)}
        />
      </div>
    </div>
  )
}
