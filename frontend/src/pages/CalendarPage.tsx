import { useRaceSchedule } from '../hooks/useRaces'
import { useUserPrefsStore } from '../store/userPrefsStore'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import { DataTable } from '../components/shared/DataTable'

export default function CalendarPage() {
  const selectedYear = useUserPrefsStore((state) => state.selectedYear)
  const { data: races, isLoading, error, refetch } = useRaceSchedule(selectedYear)

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Failed to load race calendar" onRetry={refetch} />

  const columns = [
    { header: 'Round', accessor: 'round' as const },
    { header: 'Race Name', accessor: 'raceName' as const },
    { header: 'Circuit', accessor: (row: typeof races[0]) => row.Circuit.circuitName },
    { header: 'Location', accessor: (row: typeof races[0]) => `${row.Circuit.Location.locality}, ${row.Circuit.Location.country}` },
    { header: 'Date', accessor: 'date' as const },
    { header: 'Time', accessor: (row: typeof races[0]) => row.time || '-' },
  ]

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Race Calendar - {selectedYear}</h1>
      
      <div className="mb-4 text-gray-600">
        {races?.length || 0} races scheduled
      </div>

      <DataTable data={races || []} columns={columns} />
    </div>
  )
}
