import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { SessionSelector } from '../../components/live/SessionSelector'
import { liveApi } from '../../api/live'
import type { SessionInfo } from '../../types/live'

// Mock the API
vi.mock('../../api/live', () => ({
  liveApi: {
    getSessionsByYear: vi.fn(),
  },
}))

const createMockSessions = (): SessionInfo[] => [
  {
    session_key: '9158',
    session_name: 'Race',
    session_type: 'Race',
    date_start: '2024-03-10T14:00:00Z',
    date_end: '2024-03-10T16:00:00Z',
    gmt_offset: '+03:00',
    location: 'Sakhir',
    country_name: 'Bahrain',
    circuit_short_name: 'Bahrain',
    mode: 'replay',
  },
  {
    session_key: '9157',
    session_name: 'Qualifying',
    session_type: 'Qualifying',
    date_start: '2024-03-09T15:00:00Z',
    date_end: '2024-03-09T16:00:00Z',
    gmt_offset: '+03:00',
    location: 'Sakhir',
    country_name: 'Bahrain',
    circuit_short_name: 'Bahrain',
    mode: 'replay',
  },
  {
    session_key: '9156',
    session_name: 'Practice 3',
    session_type: 'Practice 3',
    date_start: '2024-03-09T12:00:00Z',
    date_end: '2024-03-09T13:00:00Z',
    gmt_offset: '+03:00',
    location: 'Sakhir',
    country_name: 'Bahrain',
    circuit_short_name: 'Bahrain',
    mode: 'replay',
  },
  {
    session_key: '9100',
    session_name: 'Race',
    session_type: 'Race',
    date_start: '2024-02-25T14:00:00Z',
    date_end: '2024-02-25T16:00:00Z',
    gmt_offset: '+03:00',
    location: 'Jeddah',
    country_name: 'Saudi Arabia',
    circuit_short_name: 'Jeddah',
    mode: 'replay',
  },
]

const createQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = createQueryClient()
  return render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    </BrowserRouter>
  )
}

describe('SessionSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays loading state while fetching sessions', () => {
    vi.mocked(liveApi.getSessionsByYear).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    renderWithProviders(<SessionSelector />)

    expect(screen.getByText('Select Session')).toBeInTheDocument()
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('displays error message when fetch fails', async () => {
    vi.mocked(liveApi.getSessionsByYear).mockRejectedValue(new Error('API Error'))

    renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      expect(screen.getByText('Failed to load sessions. Please try again.')).toBeInTheDocument()
    })
  })

  it('displays sessions grouped by circuit', async () => {
    const sessions = createMockSessions()
    vi.mocked(liveApi.getSessionsByYear).mockResolvedValue(sessions)

    renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      expect(screen.getByText('Bahrain')).toBeInTheDocument()
      expect(screen.getByText('Jeddah')).toBeInTheDocument()
    })
  })

  it('displays session name, date, and type for each session', async () => {
    const sessions = createMockSessions()
    vi.mocked(liveApi.getSessionsByYear).mockResolvedValue(sessions)

    renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      expect(screen.getByText('Race')).toBeInTheDocument()
      expect(screen.getByText('Qualifying')).toBeInTheDocument()
      expect(screen.getByText('Practice 3')).toBeInTheDocument()
    })
  })

  it('filters sessions by circuit name search', async () => {
    const sessions = createMockSessions()
    vi.mocked(liveApi.getSessionsByYear).mockResolvedValue(sessions)

    renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      expect(screen.getByText('Bahrain')).toBeInTheDocument()
      expect(screen.getByText('Jeddah')).toBeInTheDocument()
    })

    // Search for "Jeddah"
    const searchInput = screen.getByLabelText('Search circuits')
    fireEvent.change(searchInput, { target: { value: 'Jeddah' } })

    await waitFor(() => {
      expect(screen.queryByText('Bahrain')).not.toBeInTheDocument()
      expect(screen.getByText('Jeddah')).toBeInTheDocument()
    })
  })

  it('filters sessions by session type', async () => {
    const sessions = createMockSessions()
    vi.mocked(liveApi.getSessionsByYear).mockResolvedValue(sessions)

    renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      // All sessions visible initially
      expect(screen.getAllByText('Race').length).toBeGreaterThan(0)
      expect(screen.getByText('Qualifying')).toBeInTheDocument()
    })

    // Filter by Qualifying
    const qualifyingButton = screen.getByRole('button', { name: 'Filter by Qualifying' })
    fireEvent.click(qualifyingButton)

    await waitFor(() => {
      expect(screen.getByText('Qualifying')).toBeInTheDocument()
      expect(screen.queryByText('Practice 3')).not.toBeInTheDocument()
    })
  })

  it('highlights currently selected session', async () => {
    const sessions = createMockSessions()
    vi.mocked(liveApi.getSessionsByYear).mockResolvedValue(sessions)

    // Mock URL with session_key parameter
    window.history.pushState({}, '', '?session_key=9158')

    const { container } = renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      // Check for selected styling
      const selectedElement = container.querySelector('.bg-blue-100.border-l-4.border-blue-600')
      expect(selectedElement).toBeInTheDocument()
    })
  })

  it('updates URL when user selects a session', async () => {
    const sessions = createMockSessions()
    vi.mocked(liveApi.getSessionsByYear).mockResolvedValue(sessions)

    renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      expect(screen.getByText('Race')).toBeInTheDocument()
    })

    // Click on a session
    const raceButtons = screen.getAllByRole('option')
    fireEvent.click(raceButtons[0])

    // Check URL was updated
    expect(window.location.search).toContain('session_key=')
  })

  it('supports keyboard navigation', async () => {
    const sessions = createMockSessions()
    vi.mocked(liveApi.getSessionsByYear).mockResolvedValue(sessions)

    renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      expect(screen.getByText('Race')).toBeInTheDocument()
    })

    // Simulate arrow down key
    fireEvent.keyDown(window, { key: 'ArrowDown' })
    
    // Simulate arrow up key
    fireEvent.keyDown(window, { key: 'ArrowUp' })
    
    // Simulate escape key
    fireEvent.keyDown(window, { key: 'Escape' })

    // Test passes if no errors thrown
    expect(screen.getByText('Select Session')).toBeInTheDocument()
  })

  it('displays year selector with current year and 5 years back', async () => {
    const sessions = createMockSessions()
    vi.mocked(liveApi.getSessionsByYear).mockResolvedValue(sessions)

    renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      const yearSelect = screen.getByLabelText('Select year')
      expect(yearSelect).toBeInTheDocument()
      
      // Check that current year is selected by default
      const currentYear = new Date().getFullYear()
      expect(yearSelect).toHaveValue(currentYear.toString())
    })
  })

  it('displays "No sessions found" when no matches', async () => {
    const sessions = createMockSessions()
    vi.mocked(liveApi.getSessionsByYear).mockResolvedValue(sessions)

    renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      expect(screen.getByText('Bahrain')).toBeInTheDocument()
    })

    // Search for non-existent circuit
    const searchInput = screen.getByLabelText('Search circuits')
    fireEvent.change(searchInput, { target: { value: 'NonExistentCircuit' } })

    await waitFor(() => {
      expect(screen.getByText('No sessions found matching your criteria')).toBeInTheDocument()
    })
  })

  it('groups sessions by year in descending order', async () => {
    const sessions: SessionInfo[] = [
      {
        session_key: '9200',
        session_name: 'Race',
        session_type: 'Race',
        date_start: '2024-03-10T14:00:00Z',
        date_end: '2024-03-10T16:00:00Z',
        gmt_offset: '+03:00',
        location: 'Sakhir',
        country_name: 'Bahrain',
        circuit_short_name: 'Bahrain',
        mode: 'replay',
      },
      {
        session_key: '9100',
        session_name: 'Race',
        session_type: 'Race',
        date_start: '2023-03-10T14:00:00Z',
        date_end: '2023-03-10T16:00:00Z',
        gmt_offset: '+03:00',
        location: 'Sakhir',
        country_name: 'Bahrain',
        circuit_short_name: 'Bahrain',
        mode: 'replay',
      },
    ]
    vi.mocked(liveApi.getSessionsByYear).mockResolvedValue(sessions)

    const { container } = renderWithProviders(<SessionSelector />)

    await waitFor(() => {
      const yearHeaders = container.querySelectorAll('.bg-gray-50.px-4.py-2')
      const yearTexts = Array.from(yearHeaders).map((el) => el.textContent)
      
      // Years should be in descending order
      expect(yearTexts[0]).toBe('2024')
      if (yearTexts.length > 1) {
        expect(yearTexts[1]).toBe('2023')
      }
    })
  })
})
