import { useState } from 'react'
import { useDriverStandings } from '../hooks/useStandings'
import { useUserPrefsStore } from '../store/userPrefsStore'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import { DataTable } from '../components/shared/DataTable'
import { RadarChart } from '../components/charts/RadarChart'
import { CHART_COLORS } from '../utils/constants'

export default function HeadToHeadPage() {
  const selectedYear = useUserPrefsStore((state) => state.selectedYear)
  const { data: standings, isLoading, error, refetch } = useDriverStandings(selectedYear)
  
  const [driver1Id, setDriver1Id] = useState<string>('')
  const [driver2Id, setDriver2Id] = useState<string>('')

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Failed to load driver data" onRetry={refetch} />

  const driver1 = standings?.find(s => s.Driver.driverId === driver1Id)
  const driver2 = standings?.find(s => s.Driver.driverId === driver2Id)

  const comparisonData = driver1 && driver2 ? [
    {
      header: 'Metric',
      driver1: `${driver1.Driver.givenName} ${driver1.Driver.familyName}`,
      driver2: `${driver2.Driver.givenName} ${driver2.Driver.familyName}`,
    },
    {
      header: 'Position',
      driver1: driver1.position,
      driver2: driver2.position,
    },
    {
      header: 'Points',
      driver1: driver1.points,
      driver2: driver2.points,
    },
    {
      header: 'Wins',
      driver1: driver1.wins,
      driver2: driver2.wins,
    },
    {
      header: 'Team',
      driver1: driver1.Constructors[0]?.name || '-',
      driver2: driver2.Constructors[0]?.name || '-',
    },
  ] : []

  const radarData = driver1 && driver2 ? [
    {
      r: [
        parseFloat(driver1.points),
        parseFloat(driver1.wins) * 10,
        100 - parseFloat(driver1.position) * 5,
      ],
      theta: ['Points', 'Wins (x10)', 'Position Score'],
      name: `${driver1.Driver.givenName} ${driver1.Driver.familyName}`,
      line: { color: CHART_COLORS[0] },
      fillcolor: CHART_COLORS[0] + '40',
    },
    {
      r: [
        parseFloat(driver2.points),
        parseFloat(driver2.wins) * 10,
        100 - parseFloat(driver2.position) * 5,
      ],
      theta: ['Points', 'Wins (x10)', 'Position Score'],
      name: `${driver2.Driver.givenName} ${driver2.Driver.familyName}`,
      line: { color: CHART_COLORS[1] },
      fillcolor: CHART_COLORS[1] + '40',
    },
  ] : []

  const columns = [
    { header: 'Metric', accessor: 'header' as const },
    { header: comparisonData[0]?.driver1 || 'Driver 1', accessor: 'driver1' as const },
    { header: comparisonData[0]?.driver2 || 'Driver 2', accessor: 'driver2' as const },
  ]

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Head to Head Comparison - {selectedYear}</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div>
          <label htmlFor="driver1-select" className="block text-sm font-medium text-gray-700 mb-2">
            Select Driver 1
          </label>
          <select
            id="driver1-select"
            value={driver1Id}
            onChange={(e) => setDriver1Id(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-f1-red focus:border-f1-red"
          >
            <option value="">-- Select Driver --</option>
            {standings?.map((standing) => (
              <option key={standing.Driver.driverId} value={standing.Driver.driverId}>
                {standing.Driver.givenName} {standing.Driver.familyName}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="driver2-select" className="block text-sm font-medium text-gray-700 mb-2">
            Select Driver 2
          </label>
          <select
            id="driver2-select"
            value={driver2Id}
            onChange={(e) => setDriver2Id(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-f1-red focus:border-f1-red"
          >
            <option value="">-- Select Driver --</option>
            {standings?.map((standing) => (
              <option key={standing.Driver.driverId} value={standing.Driver.driverId}>
                {standing.Driver.givenName} {standing.Driver.familyName}
              </option>
            ))}
          </select>
        </div>
      </div>

      {driver1 && driver2 ? (
        <>
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Comparison Table</h2>
            <DataTable data={comparisonData.slice(1)} columns={columns} />
          </div>

          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Performance Radar</h2>
            <RadarChart
              data={radarData}
              title="Driver Performance Comparison"
              height={500}
            />
          </div>
        </>
      ) : (
        <div className="text-center py-8 text-gray-500">
          Select two drivers to compare
        </div>
      )}
    </div>
  )
}
