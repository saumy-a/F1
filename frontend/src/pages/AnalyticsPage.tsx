import { useState } from 'react'
import { useUserPrefsStore } from '../store/userPrefsStore'
import { useDriverStandings } from '../hooks/useStandings'
import { LoadingSpinner } from '../components/shared/LoadingSpinner'
import { ErrorMessage } from '../components/shared/ErrorMessage'
import {
  usePerformanceTrends,
  useConsistencyScore,
  useFormIndicator,
  useDNFRate,
  useDriverComparison,
} from '../hooks/useAnalytics'
import { LineChart } from '../components/charts/LineChart'
import { RadarChart } from '../components/charts/RadarChart'
import { HorizontalBarChart } from '../components/charts/HorizontalBarChart'
import { DataTable } from '../components/shared/DataTable'
import { CHART_COLORS } from '../utils/constants'

type TabType = 'driver' | 'team' | 'circuit' | 'comparative'

export default function AnalyticsPage() {
  const selectedYear = useUserPrefsStore((state) => state.selectedYear)
  const [activeTab, setActiveTab] = useState<TabType>('driver')
  const [selectedDriver, setSelectedDriver] = useState<string>('')
  const [comparisonDrivers, setComparisonDrivers] = useState<string[]>([])

  // Fetch driver standings to populate driver selector
  const { data: standings, isLoading: standingsLoading } = useDriverStandings(selectedYear)

  const tabs = [
    { id: 'driver' as TabType, label: 'Driver Analytics' },
    { id: 'team' as TabType, label: 'Team Analytics' },
    { id: 'circuit' as TabType, label: 'Circuit Analytics' },
    { id: 'comparative' as TabType, label: 'Comparative Analytics' },
  ]

  return (
    <div className="p-6">
      <h1 className="text-3xl font-display text-f1-white tracking-wider uppercase mb-6">Advanced Analytics - {selectedYear}</h1>

      {/* Tab Navigation */}
      <div className="border-b border-f1-border mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                py-4 px-1 border-b-2 font-medium text-sm transition-colors
                ${
                  activeTab === tab.id
                    ? 'border-red-600 text-red-600'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-f1-border'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Driver Selector */}
      {(activeTab === 'driver' || activeTab === 'comparative') && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            {activeTab === 'driver' ? 'Select Driver' : 'Select Drivers (2-5)'}
          </label>
          {standingsLoading ? (
            <LoadingSpinner />
          ) : (
            <>
              {activeTab === 'driver' ? (
                <select
                  value={selectedDriver}
                  onChange={(e) => setSelectedDriver(e.target.value)}
                  className="block w-full max-w-md px-3 py-2 border border-f1-border rounded-md shadow-sm focus:outline-none focus:ring-red-500 focus:border-red-500"
                >
                  <option value="">-- Select a driver --</option>
                  {standings?.map((s) => (
                    <option key={s.Driver.driverId} value={s.Driver.driverId}>
                      {s.Driver.givenName} {s.Driver.familyName}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="space-y-2">
                  {standings?.slice(0, 10).map((s) => (
                    <label key={s.Driver.driverId} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={comparisonDrivers.includes(s.Driver.driverId)}
                        onChange={(e) => {
                          if (e.target.checked && comparisonDrivers.length < 5) {
                            setComparisonDrivers([...comparisonDrivers, s.Driver.driverId])
                          } else if (!e.target.checked) {
                            setComparisonDrivers(
                              comparisonDrivers.filter((id) => id !== s.Driver.driverId)
                            )
                          }
                        }}
                        disabled={
                          !comparisonDrivers.includes(s.Driver.driverId) &&
                          comparisonDrivers.length >= 5
                        }
                        className="rounded border-f1-border text-red-600 focus:ring-red-500"
                      />
                      <span className="text-sm">
                        {s.Driver.givenName} {s.Driver.familyName}
                      </span>
                    </label>
                  ))}
                  {comparisonDrivers.length > 0 && (
                    <p className="text-xs text-gray-400 mt-2">
                      {comparisonDrivers.length} of 5 drivers selected
                    </p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Tab Content */}
      {activeTab === 'driver' && (
        <DriverAnalyticsSection driverId={selectedDriver} year={selectedYear} />
      )}
      {activeTab === 'team' && <TeamAnalyticsSection year={selectedYear} />}
      {activeTab === 'circuit' && <CircuitAnalyticsSection year={selectedYear} />}
      {activeTab === 'comparative' && (
        <ComparativeAnalyticsSection driverIds={comparisonDrivers} year={selectedYear} />
      )}
    </div>
  )
}

// Driver Analytics Section Component
function DriverAnalyticsSection({ driverId, year }: { driverId: string; year: string }) {
  const {
    data: trends,
    isLoading: trendsLoading,
    error: trendsError,
  } = usePerformanceTrends(driverId, year)
  const {
    data: consistency,
    isLoading: consistencyLoading,
    error: consistencyError,
  } = useConsistencyScore(driverId, year)
  const { data: form, isLoading: formLoading, error: formError } = useFormIndicator(driverId, year)
  const { data: dnf, isLoading: dnfLoading, error: dnfError } = useDNFRate(driverId, year)

  if (!driverId) {
    return (
      <div className="text-center py-12 text-gray-400">
        Please select a driver to view analytics
      </div>
    )
  }

  const isLoading = trendsLoading || consistencyLoading || formLoading || dnfLoading
  
  // Check if consistency error is 422 (insufficient data) - this is expected and not critical
  const isConsistency422 = consistencyError && 
    (consistencyError as any)?.response?.status === 422
  
  // Only show error if it's not a 422 consistency error
  const hasCriticalError = trendsError || formError || dnfError || 
    (consistencyError && !isConsistency422)

  if (isLoading) return <LoadingSpinner />
  if (hasCriticalError)
    return <ErrorMessage message="Failed to load driver analytics. Please try again." />

  return (
    <div className="space-y-8">
      {/* Performance Trends */}
      {trends && (
        <div className="bg-transparent p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Performance Trends</h2>
          <LineChart
            data={[
              {
                x: trends.data.map((d: any) => d.round),
                y: trends.data.map((d: any) => d.metric_value),
                name: 'Position',
                mode: 'lines+markers',
                line: { color: CHART_COLORS[0] },
              },
            ]}
            title="Race Position Over Season"
            xAxisTitle="Round"
            yAxisTitle="Position"
            height={400}
          />
        </div>
      )}

      {/* Consistency Score */}
      {consistency && (
        <div className="bg-transparent p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Consistency Score</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-[#292a2c]/40 rounded">
              <div className="text-3xl font-display text-f1-white tracking-wider uppercase text-red-600">{consistency.consistency_score.toFixed(1)}</div>
              <div className="text-sm text-gray-400 mt-1">Consistency Score</div>
            </div>
            <div className="text-center p-4 bg-[#292a2c]/40 rounded">
              <div className="text-3xl font-display text-f1-white tracking-wider uppercase text-gray-300">
                {consistency.avg_position.toFixed(1)}
              </div>
              <div className="text-sm text-gray-400 mt-1">Average Position</div>
            </div>
            <div className="text-center p-4 bg-[#292a2c]/40 rounded">
              <div className="text-3xl font-display text-f1-white tracking-wider uppercase text-gray-300">
                {consistency.std_dev.toFixed(2)}
              </div>
              <div className="text-sm text-gray-400 mt-1">Standard Deviation</div>
            </div>
          </div>
        </div>
      )}
      
      {/* Consistency Score - Insufficient Data Message */}
      {!consistency && isConsistency422 && (
        <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-2 text-yellow-800">Consistency Score</h2>
          <p className="text-yellow-700">
            Insufficient data to calculate consistency score. At least 5 completed races are required.
          </p>
        </div>
      )}

      {/* Form Indicator */}
      {form && (
        <div className="bg-transparent p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Form</h2>
          <div className="flex items-center space-x-4">
            <div className="text-2xl font-display text-f1-white tracking-wider uppercase">
              Trend:{' '}
              <span
                className={
                  form.trend_direction === 'improving'
                    ? 'text-green-600'
                    : form.trend_direction === 'declining'
                    ? 'text-red-600'
                    : 'text-gray-400'
                }
              >
                {form.trend_direction === 'improving' ? '↑' : form.trend_direction === 'declining' ? '↓' : '→'}{' '}
                {form.trend_direction.toUpperCase()}
              </span>
            </div>
            <div className="text-gray-400">
              Average: {form.avg_position.toFixed(1)}
            </div>
          </div>
        </div>
      )}

      {/* DNF Rate */}
      {dnf && (
        <div className="bg-transparent p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">DNF Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-[#292a2c]/40 rounded">
              <div className="text-3xl font-display text-f1-white tracking-wider uppercase text-red-600">
                {dnf.dnf_percentage.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-400 mt-1">DNF Rate</div>
            </div>
            <div className="text-center p-4 bg-[#292a2c]/40 rounded">
              <div className="text-3xl font-display text-f1-white tracking-wider uppercase text-gray-300">{dnf.dnf_count}</div>
              <div className="text-sm text-gray-400 mt-1">DNFs</div>
            </div>
            <div className="text-center p-4 bg-[#292a2c]/40 rounded">
              <div className="text-3xl font-display text-f1-white tracking-wider uppercase text-gray-300">{dnf.total_races}</div>
              <div className="text-sm text-gray-400 mt-1">Total Races</div>
            </div>
          </div>
          <HorizontalBarChart
            data={{
              x: [dnf.dnf_count, dnf.total_races - dnf.dnf_count],
              y: ['DNF', 'Finished'],
              text: [dnf.dnf_count.toString(), (dnf.total_races - dnf.dnf_count).toString()],
              marker: { color: [CHART_COLORS[0], CHART_COLORS[3]] },
            }}
            title="Race Completion"
            xAxisTitle="Count"
            height={200}
          />
        </div>
      )}
    </div>
  )
}

// Team Analytics Section Component
function TeamAnalyticsSection({ year }: { year: string }) {
  return (
    <div className="text-center py-12 text-gray-400">
      Team analytics coming soon. This will include team reliability, constructor development, and
      driver pairing analysis.
    </div>
  )
}

// Circuit Analytics Section Component
function CircuitAnalyticsSection({ year }: { year: string }) {
  return (
    <div className="text-center py-12 text-gray-400">
      Circuit analytics coming soon. This will include circuit performance and difficulty metrics.
    </div>
  )
}

// Comparative Analytics Section Component
function ComparativeAnalyticsSection({
  driverIds,
  year,
}: {
  driverIds: string[]
  year: string
}) {
  const {
    data: comparison,
    isLoading,
    error,
  } = useDriverComparison(driverIds, year)

  if (driverIds.length < 2) {
    return (
      <div className="text-center py-12 text-gray-400">
        Please select at least 2 drivers to compare
      </div>
    )
  }

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Failed to load comparison data. Please try again." />

  if (!comparison) return null

  // Prepare radar chart data
  const radarData = comparison.drivers.map((driver, idx) => ({
    r: Object.values(comparison.metrics).map((values) => values[idx] || 0),
    theta: Object.keys(comparison.metrics),
    name: driver,
    fill: 'toself' as const,
    line: { color: CHART_COLORS[idx % CHART_COLORS.length] },
  }))

  // Prepare table data
  const tableData = comparison.drivers.map((driver, idx) => ({
    driver,
    ...Object.fromEntries(
      Object.entries(comparison.metrics).map(([key, values]) => [key, values[idx]?.toFixed(2)])
    ),
  }))

  const tableColumns = [
    { header: 'Driver', accessor: 'driver' as const },
    ...Object.keys(comparison.metrics).map((key) => ({
      header: key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
      accessor: key as any,
    })),
  ]

  return (
    <div className="space-y-8">
      {/* Radar Chart */}
      <div className="bg-transparent p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Multi-Dimensional Comparison</h2>
        <RadarChart data={radarData} title="Driver Performance Metrics" height={500} />
      </div>

      {/* Comparison Table */}
      <div className="bg-transparent p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Side-by-Side Metrics</h2>
        <DataTable data={tableData} columns={tableColumns} />
      </div>

      {/* Championship Projection - Placeholder */}
      <div className="bg-transparent p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Championship Projection</h2>
        <p className="text-gray-400">
          Championship projection visualization will be displayed here.
        </p>
      </div>
    </div>
  )
}
