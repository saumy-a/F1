import { useConstructorStandings } from '../hooks/useStandings'
import { useUserPrefsStore } from '../store/userPrefsStore'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import { DataTable } from '../components/shared/DataTable'
import { HorizontalBarChart } from '../components/charts/HorizontalBarChart'
import { CHART_COLORS } from '../utils/constants'

export default function ConstructorStandingsPage() {
  const selectedYear = useUserPrefsStore((state) => state.selectedYear)
  const { data: standings, isLoading, error, refetch } = useConstructorStandings(selectedYear)

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Failed to load constructor standings" onRetry={refetch} />
  if (!standings || standings.length === 0) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-display text-f1-white tracking-wider uppercase mb-6">Constructor Standings - {selectedYear}</h1>
        <div className="text-center py-12 text-gray-400">
          No constructor standings data available for {selectedYear}
        </div>
      </div>
    )
  }

  const columns = [
    { header: 'Position', accessor: 'position' as const },
    { 
      header: 'Constructor', 
      accessor: (row: any) => row.Constructor?.name || '-' 
    },
    { 
      header: 'Nationality', 
      accessor: (row: any) => row.Constructor?.nationality || '-' 
    },
    { header: 'Points', accessor: 'points' as const, className: 'font-semibold' },
    { header: 'Wins', accessor: 'wins' as const },
  ]

  const chartData = {
    x: standings.map(s => parseFloat(s.points)),
    y: standings.map(s => s.Constructor.name),
    text: standings.map(s => s.points),
    marker: {
      color: CHART_COLORS,
    },
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-display text-f1-white tracking-wider uppercase mb-6">Constructor Standings - {selectedYear}</h1>
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Standings Table</h2>
        <DataTable data={standings} columns={columns} />
      </div>

      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Points Distribution</h2>
        <HorizontalBarChart
          data={chartData}
          title="Constructor Championship Points"
          xAxisTitle="Points"
          yAxisTitle="Constructor"
          height={Math.max(400, standings.length * 40)}
        />
      </div>
    </div>
  )
}
