import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import DriverStandingsPage from '../../pages/DriverStandingsPage'

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
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  )
}

describe('DriverStandingsPage', () => {
  it('renders loading state initially', () => {
    renderWithClient(<DriverStandingsPage />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('renders driver standings table with data', async () => {
    renderWithClient(<DriverStandingsPage />)

    await waitFor(() => {
      expect(screen.getByText('Driver Standings - 2024')).toBeInTheDocument()
    })

    expect(screen.getByText('Max Verstappen')).toBeInTheDocument()
    expect(screen.getByText('Sergio Pérez')).toBeInTheDocument()
    expect(screen.getByText('575')).toBeInTheDocument()
    expect(screen.getByText('285')).toBeInTheDocument()
  })

  it('renders chart component', async () => {
    renderWithClient(<DriverStandingsPage />)

    await waitFor(() => {
      expect(screen.getByTestId('plotly-chart')).toBeInTheDocument()
    })
  })

  it('displays error message on API failure', async () => {
    server.use(
      http.get('http://localhost:8000/api/standings/drivers/:year', () => {
        return HttpResponse.json({ error: 'Server error' }, { status: 500 })
      })
    )

    renderWithClient(<DriverStandingsPage />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load driver standings')).toBeInTheDocument()
    })
  })

  it('displays retry button on error', async () => {
    server.use(
      http.get('http://localhost:8000/api/standings/drivers/:year', () => {
        return HttpResponse.json({ error: 'Server error' }, { status: 500 })
      })
    )

    renderWithClient(<DriverStandingsPage />)

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()
    })
  })

  it('displays table headers correctly', async () => {
    renderWithClient(<DriverStandingsPage />)

    await waitFor(() => {
      expect(screen.getByText('Position')).toBeInTheDocument()
      expect(screen.getByText('Driver')).toBeInTheDocument()
      expect(screen.getByText('Nationality')).toBeInTheDocument()
      expect(screen.getByText('Team')).toBeInTheDocument()
      expect(screen.getByText('Points')).toBeInTheDocument()
      expect(screen.getByText('Wins')).toBeInTheDocument()
    })
  })
})
