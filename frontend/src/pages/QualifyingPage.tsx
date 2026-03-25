import { useState, useEffect } from 'react'
import { useRaceSchedule, useQualifyingResults } from '../hooks/useRaces'
import { useUserPrefsStore } from '../store/userPrefsStore'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import { DataTable } from '../components/shared/DataTable'

export default function QualifyingPage() {
  const selectedYear = useUserPrefsStore((state) => state.selectedYear)
  const { data: races } = useRaceSchedule(selectedYear)
  const [selectedRound, setSelectedRound] = useState<string>('1')
  
  // Update selectedRound when races load
  useEffect(() => {
    if (races && races.length > 0 && !races.find(r => r.round === selectedRound)) {
      setSelectedRound(races[0].round)
    }
  }, [races, selectedRound])
  
  const { data: qualifyingResult, isLoading, error, refetch } = useQualifyingResults(
    selectedYear,
    parseInt(selectedRound)
  )

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Failed to load qualifying results" onRetry={refetch} />
  if (!qualifyingResult) return <div className="p-6">No qualifying results available</div>

  const columns = [
    { header: 'Pos', accessor: 'position' as const },
    { 
      header: 'Driver', 
      accessor: (row: typeof qualifyingResult.QualifyingResults[0]) => `${row.Driver.givenName} ${row.Driver.familyName}` 
    },
    { header: 'Team', accessor: (row: typeof qualifyingResult.QualifyingResults[0]) => row.Constructor.name },
    { header: 'Q1', accessor: (row: typeof qualifyingResult.QualifyingResults[0]) => row.Q1 || '-' },
    { header: 'Q2', accessor: (row: typeof qualifyingResult.QualifyingResults[0]) => row.Q2 || '-' },
    { header: 'Q3', accessor: (row: typeof qualifyingResult.QualifyingResults[0]) => row.Q3 || '-', className: 'font-semibold' },
  ]

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Qualifying Results - {selectedYear}</h1>
      
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

      <div className="mb-4">
        <h2 className="text-xl font-semibold">{qualifyingResult.raceName}</h2>
        <p className="text-gray-600">
          {qualifyingResult.Circuit.circuitName} - {qualifyingResult.date}
        </p>
      </div>

      <DataTable data={qualifyingResult.QualifyingResults} columns={columns} />
    </div>
  )
}
