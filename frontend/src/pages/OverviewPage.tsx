import { useDriverStandings, useConstructorStandings } from '../hooks/useStandings'
import { useRaceSchedule, useRaceResults } from '../hooks/useRaces'
import { useUserPrefsStore } from '../store/userPrefsStore'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import { Link } from 'react-router-dom'

export default function OverviewPage() {
  const selectedYear = useUserPrefsStore((state) => state.selectedYear)
  const { data: races, isLoading: racesLoading } = useRaceSchedule(selectedYear)
  const { data: driverStandings, isLoading: driversLoading } = useDriverStandings(selectedYear)
  const { data: constructorStandings, isLoading: constructorsLoading } = useConstructorStandings(selectedYear)

  const nextRace = races?.find(race => new Date(race.date) > new Date())
  const latestRace = races?.[races.length - 1]
  const latestRaceRound = latestRace?.round ? parseInt(latestRace.round) : undefined
  
  const { data: latestResults, isLoading: resultsLoading } = useRaceResults(
    selectedYear,
    latestRaceRound || 0
  )

  const isLoading = racesLoading || driversLoading || constructorsLoading

  if (isLoading) return <LoadingSpinner />

  const topDrivers = driverStandings?.slice(0, 5)
  const topConstructors = constructorStandings?.slice(0, 3)
  const topThreeResults = latestResults?.Results?.slice(0, 3)

  return (
    <div className="p-6">
      <h1 className="text-3xl font-display text-f1-white tracking-wider uppercase mb-6">F1 Dashboard Overview - {selectedYear}</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Next Race Card */}
        <div className="f1-panel p-6">
          <h2 className="text-xl font-semibold mb-4">Next Race</h2>
          {nextRace ? (
            <div>
              <p className="text-lg font-medium text-red-600">{nextRace.raceName}</p>
              <p className="text-gray-400">{nextRace.Circuit.circuitName}</p>
              <p className="text-gray-400">
                {nextRace.Circuit.Location.locality}, {nextRace.Circuit.Location.country}
              </p>
              <p className="text-sm text-gray-400 mt-2">
                {nextRace.date} {nextRace.time && `at ${nextRace.time}`}
              </p>
            </div>
          ) : (
            <p className="text-gray-400">No upcoming races</p>
          )}
        </div>

        {/* Latest Race Card */}
        <div className="f1-panel p-6">
          <h2 className="text-xl font-semibold mb-4">Latest Race</h2>
          {latestRace ? (
            <div>
              <p className="text-lg font-medium text-red-600">{latestRace.raceName}</p>
              <p className="text-gray-400">{latestRace.Circuit.circuitName}</p>
              <p className="text-gray-400">
                {latestRace.Circuit.Location.locality}, {latestRace.Circuit.Location.country}
              </p>
              <p className="text-sm text-gray-400 mt-2">{latestRace.date}</p>
            </div>
          ) : (
            <p className="text-gray-400">No race data available</p>
          )}
        </div>
      </div>

      {/* Latest Results Section */}
      {topThreeResults && topThreeResults.length > 0 && (
        <div className="f1-panel p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Latest Results - {latestRace?.raceName}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {topThreeResults.map((result, index) => {
              const podiumColors = ['bg-yellow-100 border-yellow-400', 'bg-gray-100 border-gray-400', 'bg-orange-100 border-orange-400']
              const podiumLabels = ['🥇 1st Place', '🥈 2nd Place', '🥉 3rd Place']
              return (
                <div key={result.position} className={`border-2 rounded-lg p-4 ${podiumColors[index]}`}>
                  <p className="text-sm font-semibold text-gray-400 mb-2">{podiumLabels[index]}</p>
                  <p className="text-lg font-bold">
                    {result.Driver.givenName} {result.Driver.familyName}
                  </p>
                  <p className="text-sm text-gray-400">{result.Constructor.name}</p>
                  <p className="text-sm text-gray-400 mt-2">
                    Time: {result.Time?.time || result.status}
                  </p>
                  <p className="text-sm font-semibold text-red-600 mt-1">
                    {result.points} points
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Driver Standings Preview */}
        <div className="f1-panel p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Driver Standings (Top 5)</h2>
            <Link to="/standings/drivers" className="text-red-600 hover:text-red-700 text-sm font-medium">
              View Full Standings →
            </Link>
          </div>
          {topDrivers && topDrivers.length > 0 ? (
            <div className="space-y-2">
              {topDrivers.map((driver) => (
                <div key={driver.position} className="flex justify-between items-center py-2 border-b">
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-gray-400 w-6">{driver.position}</span>
                    <span className="font-medium">
                      {driver.Driver.givenName} {driver.Driver.familyName}
                    </span>
                  </div>
                  <span className="font-semibold text-red-600">{driver.points} pts</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No standings data available</p>
          )}
        </div>

        {/* Constructor Standings Preview */}
        <div className="f1-panel p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Constructor Standings (Top 3)</h2>
            <Link to="/standings/constructors" className="text-red-600 hover:text-red-700 text-sm font-medium">
              View Full Standings →
            </Link>
          </div>
          {topConstructors && topConstructors.length > 0 ? (
            <div className="space-y-2">
              {topConstructors.map((constructor) => (
                <div key={constructor.position} className="flex justify-between items-center py-2 border-b">
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-gray-400 w-6">{constructor.position}</span>
                    <span className="font-medium">{constructor.Constructor.name}</span>
                  </div>
                  <span className="font-semibold text-red-600">{constructor.points} pts</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400">No standings data available</p>
          )}
        </div>
      </div>
    </div>
  )
}
