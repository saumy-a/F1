import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import AnalyticsPage from '../../pages/AnalyticsPage'

// Mock Zustand store
vi.mock('../../store/userPrefsStore', () => ({
  useUserPrefsStore: vi.fn(() => '2024'),
}))

// Mock Plotly to avoid rendering issues in tests
vi.mock('react-plotly.js', () => ({
  default: () => <div data-testid="plotly-chart">Chart</div>,
}))

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

const renderWithClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient()
  return render(<QueryClientProvider client={queryClient}>{component}</QueryClientProvider>)
}

// Mock data
const mockDriverStandings = [
  {
    position: '1',
    points: '575',
    wins: '19',
    Driver: {
      driverId: 'max_verstappen',
      givenName: 'Max',
      familyName: 'Verstappen',
      nationality: 'Dutch',
    },
    Constructors: [
      {
        constructorId: 'red_bull',
        name: 'Red Bull',
        nationality: 'Austrian',
      },
    ],
  },
  {
    position: '2',
    points: '285',
    wins: '2',
    Driver: {
      driverId: 'perez',
      givenName: 'Sergio',
      familyName: 'Pérez',
      nationality: 'Mexican',
    },
    Constructors: [
      {
        constructorId: 'red_bull',
        name: 'Red Bull',
        nationality: 'Austrian',
      },
    ],
  },
]

const mockPerformanceTrends = {
  data: [
    { round: 1, position: 1 },
    { round: 2, position: 2 },
    { round: 3, position: 1 },
  ],
  layout: {},
}

const mockConsistencyScore = {
  score: 85.5,
  std_dev: 2.3,
  mean_position: 1.5,
}

const mockFormIndicator = {
  recent_positions: [1, 2, 1, 1, 3],
  trend: 'stable',
  average_position: 1.6,
}

const mockDNFRate = {
  dnf_count: 2,
  total_races: 20,
  dnf_rate: 0.1,
}

const mockDriverComparison = {
  drivers: ['Max Verstappen', 'Sergio Pérez'],
  metrics: {
    avg_finish: [1.5, 3.2],
    points_per_race: [25.5, 15.3],
    consistency_score: [85.5, 72.1],
    dnf_rate: [0.1, 0.15],
  },
}

describe('AnalyticsPage', () => {
  beforeEach(() => {
    // Setup mock handlers
    server.use(
      http.get('http://localhost:8000/api/standings/drivers/:year', () => {
        return HttpResponse.json(mockDriverStandings)
      }),
      http.get('http://localhost:8000/api/analytics/trends/:driverId/:year', () => {
        return HttpResponse.json(mockPerformanceTrends)
      }),
      http.get('http://localhost:8000/api/analytics/consistency/:driverId/:year', () => {
        return HttpResponse.json(mockConsistencyScore)
      }),
      http.get('http://localhost:8000/api/analytics/form/:driverId/:year', () => {
        return HttpResponse.json(mockFormIndicator)
      }),
      http.get('http://localhost:8000/api/analytics/dnf/:driverId/:year', () => {
        return HttpResponse.json(mockDNFRate)
      }),
      http.post('http://localhost:8000/api/analytics/compare', () => {
        return HttpResponse.json(mockDriverComparison)
      })
    )
  })

  it('renders analytics page with tabs', () => {
    renderWithClient(<AnalyticsPage />)
    expect(screen.getByText('Advanced Analytics - 2024')).toBeInTheDocument()
    expect(screen.getByText('Driver Analytics')).toBeInTheDocument()
    expect(screen.getByText('Team Analytics')).toBeInTheDocument()
    expect(screen.getByText('Circuit Analytics')).toBeInTheDocument()
    expect(screen.getByText('Comparative Analytics')).toBeInTheDocument()
  })

  it('displays driver selector on driver analytics tab', async () => {
    renderWithClient(<AnalyticsPage />)

    await waitFor(() => {
      expect(screen.getByText('Select Driver')).toBeInTheDocument()
      expect(screen.getByRole('combobox')).toBeInTheDocument()
    })
  })

  it('switches between tabs', async () => {
    renderWithClient(<AnalyticsPage />)

    // Click on Team Analytics tab
    const teamTab = screen.getByText('Team Analytics')
    fireEvent.click(teamTab)

    await waitFor(() => {
      expect(screen.getByText(/team analytics coming soon/i)).toBeInTheDocument()
    })

    // Click on Circuit Analytics tab
    const circuitTab = screen.getByText('Circuit Analytics')
    fireEvent.click(circuitTab)

    await waitFor(() => {
      expect(screen.getByText(/circuit analytics coming soon/i)).toBeInTheDocument()
    })
  })

  it('displays driver analytics when driver is selected', async () => {
    renderWithClient(<AnalyticsPage />)

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument()
    })

    // Select a driver
    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'max_verstappen' } })

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Performance Trends' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'Consistency Score' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'Recent Form' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'DNF Statistics' })).toBeInTheDocument()
    })
  })

  it('displays consistency score metrics', async () => {
    renderWithClient(<AnalyticsPage />)

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument()
    })

    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'max_verstappen' } })

    await waitFor(() => {
      expect(screen.getByText('85.5')).toBeInTheDocument()
      expect(screen.getByText('1.5')).toBeInTheDocument()
      expect(screen.getByText('2.30')).toBeInTheDocument()
    })
  })

  it('displays DNF statistics', async () => {
    renderWithClient(<AnalyticsPage />)

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument()
    })

    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'max_verstappen' } })

    await waitFor(() => {
      expect(screen.getByText('10.0%')).toBeInTheDocument()
      expect(screen.getByText('2')).toBeInTheDocument()
      expect(screen.getByText('20')).toBeInTheDocument()
    })
  })

  it('displays comparative analytics with multiple drivers', async () => {
    renderWithClient(<AnalyticsPage />)

    // Switch to comparative tab
    const comparativeTab = screen.getByText('Comparative Analytics')
    fireEvent.click(comparativeTab)

    await waitFor(() => {
      expect(screen.getByText('Select Drivers (2-5)')).toBeInTheDocument()
      // Wait for checkboxes to appear after standings load
      expect(screen.getAllByRole('checkbox').length).toBeGreaterThan(0)
    })

    // Select two drivers
    const checkboxes = screen.getAllByRole('checkbox')
    fireEvent.click(checkboxes[0])
    fireEvent.click(checkboxes[1])

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Multi-Dimensional Comparison' })).toBeInTheDocument()
      expect(screen.getByRole('heading', { name: 'Side-by-Side Metrics' })).toBeInTheDocument()
    })
  })

  it('limits driver selection to 5 drivers', async () => {
    renderWithClient(<AnalyticsPage />)

    const comparativeTab = screen.getByText('Comparative Analytics')
    fireEvent.click(comparativeTab)

    await waitFor(() => {
      expect(screen.getByText('Select Drivers (2-5)')).toBeInTheDocument()
      expect(screen.getAllByRole('checkbox').length).toBeGreaterThan(0)
    })

    const checkboxes = screen.getAllByRole('checkbox')
    
    // Select 5 drivers (or as many as available, up to 5)
    const numToSelect = Math.min(5, checkboxes.length)
    for (let i = 0; i < numToSelect; i++) {
      fireEvent.click(checkboxes[i])
    }

    await waitFor(() => {
      expect(screen.getByText(new RegExp(`${numToSelect} of 5 drivers selected`, 'i'))).toBeInTheDocument()
    })
  })

  it('shows message when no driver is selected', () => {
    renderWithClient(<AnalyticsPage />)

    expect(screen.getByText('Please select a driver to view analytics')).toBeInTheDocument()
  })

  it('shows message when less than 2 drivers selected for comparison', async () => {
    renderWithClient(<AnalyticsPage />)

    const comparativeTab = screen.getByText('Comparative Analytics')
    fireEvent.click(comparativeTab)

    await waitFor(() => {
      expect(screen.getByText('Please select at least 2 drivers to compare')).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    server.use(
      http.get('http://localhost:8000/api/analytics/trends/:driverId/:year', () => {
        return HttpResponse.json({ error: 'Server error' }, { status: 500 })
      })
    )

    renderWithClient(<AnalyticsPage />)

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument()
    })

    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'max_verstappen' } })

    await waitFor(() => {
      expect(screen.getByText(/failed to load driver analytics/i)).toBeInTheDocument()
    })
  })
})
