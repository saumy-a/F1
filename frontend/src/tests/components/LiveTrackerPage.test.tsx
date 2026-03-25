import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server'
import LiveTrackerPage from '../../pages/LiveTrackerPage'
import * as useLiveDataModule from '../../hooks/useLiveData'

// Mock useLiveData hook
vi.mock('../../hooks/useLiveData')

// Mock child components to simplify testing
vi.mock('../../components/live/SessionModeIndicator', () => ({
  SessionModeIndicator: () => <div data-testid="session-mode-indicator">Mode Indicator</div>,
}))

vi.mock('../../components/live/PositionTracker', () => ({
  PositionTracker: () => <div data-testid="position-tracker">Position Tracker</div>,
}))

vi.mock('../../components/live/IntervalDisplay', () => ({
  IntervalDisplay: () => <div data-testid="interval-display">Interval Display</div>,
}))

vi.mock('../../components/live/RaceControlFeed', () => ({
  RaceControlFeed: () => <div data-testid="race-control-feed">Race Control Feed</div>,
}))

vi.mock('../../components/live/WeatherWidget', () => ({
  WeatherWidget: () => <div data-testid="weather-widget">Weather Widget</div>,
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

describe('LiveTrackerPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders loading state while fetching session data', () => {
    vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
      sessionInfo: null,
      sessionMode: null,
      isLoading: true,
      sessionError: null,
      refetchSession: vi.fn(),
      wsStatus: 'disconnected',
      isLoadingInitialData: false,
    })

    renderWithClient(<LiveTrackerPage />)
    
    expect(screen.getByText('Live Race Tracker')).toBeInTheDocument()
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('renders error message when session fetch fails', () => {
    const mockRefetch = vi.fn()
    
    vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
      sessionInfo: null,
      sessionMode: null,
      isLoading: false,
      sessionError: new Error('Failed to fetch session'),
      refetchSession: mockRefetch,
      wsStatus: 'disconnected',
      isLoadingInitialData: false,
    })

    renderWithClient(<LiveTrackerPage />)
    
    expect(screen.getByText('Live Race Tracker')).toBeInTheDocument()
    expect(screen.getByText('Failed to fetch session')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()
  })

  it('renders no active session message when sessionInfo is null', () => {
    vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
      sessionInfo: null,
      sessionMode: null,
      isLoading: false,
      sessionError: null,
      refetchSession: vi.fn(),
      wsStatus: 'disconnected',
      isLoadingInitialData: false,
    })

    renderWithClient(<LiveTrackerPage />)
    
    expect(screen.getByText('No active session')).toBeInTheDocument()
    expect(screen.getByText('Check back during a race weekend for live tracking')).toBeInTheDocument()
  })

  it('renders upcoming mode with countdown timer', () => {
    const futureDate = new Date(Date.now() + 3600000).toISOString() // 1 hour from now
    
    vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
      sessionInfo: {
        session_key: '9158',
        session_name: 'Race',
        session_type: 'Race',
        date_start: futureDate,
        date_end: new Date(Date.now() + 7200000).toISOString(),
        gmt_offset: '+00:00',
        location: 'Bahrain',
        country_name: 'Bahrain',
        circuit_short_name: 'Bahrain',
        mode: 'upcoming',
      },
      sessionMode: 'upcoming',
      isLoading: false,
      sessionError: null,
      refetchSession: vi.fn(),
      wsStatus: 'disconnected',
      isLoadingInitialData: false,
    })

    renderWithClient(<LiveTrackerPage />)
    
    expect(screen.getByText('Live Race Tracker')).toBeInTheDocument()
    expect(screen.getByText('Race - Bahrain')).toBeInTheDocument()
    expect(screen.getByText(/Session starts:/)).toBeInTheDocument()
    expect(screen.getByTestId('session-mode-indicator')).toBeInTheDocument()
  })

  it('renders live mode with all panels', () => {
    vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
      sessionInfo: {
        session_key: '9158',
        session_name: 'Race',
        session_type: 'Race',
        date_start: new Date(Date.now() - 3600000).toISOString(),
        date_end: new Date(Date.now() + 3600000).toISOString(),
        gmt_offset: '+00:00',
        location: 'Bahrain',
        country_name: 'Bahrain',
        circuit_short_name: 'Bahrain',
        mode: 'live',
      },
      sessionMode: 'live',
      isLoading: false,
      sessionError: null,
      refetchSession: vi.fn(),
      wsStatus: 'connected',
      isLoadingInitialData: false,
    })

    renderWithClient(<LiveTrackerPage />)
    
    expect(screen.getByText('Live Race Tracker')).toBeInTheDocument()
    expect(screen.getByText('Race - Bahrain')).toBeInTheDocument()
    expect(screen.getByTestId('session-mode-indicator')).toBeInTheDocument()
    expect(screen.getByTestId('position-tracker')).toBeInTheDocument()
    expect(screen.getByTestId('interval-display')).toBeInTheDocument()
    expect(screen.getByTestId('weather-widget')).toBeInTheDocument()
    expect(screen.getByTestId('race-control-feed')).toBeInTheDocument()
    expect(screen.getByText(/WebSocket: connected/)).toBeInTheDocument()
  })

  it('renders replay mode with all panels', () => {
    vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
      sessionInfo: {
        session_key: '9158',
        session_name: 'Race',
        session_type: 'Race',
        date_start: new Date(Date.now() - 7200000).toISOString(),
        date_end: new Date(Date.now() - 3600000).toISOString(),
        gmt_offset: '+00:00',
        location: 'Bahrain',
        country_name: 'Bahrain',
        circuit_short_name: 'Bahrain',
        mode: 'replay',
      },
      sessionMode: 'replay',
      isLoading: false,
      sessionError: null,
      refetchSession: vi.fn(),
      wsStatus: 'disconnected',
      isLoadingInitialData: false,
    })

    renderWithClient(<LiveTrackerPage />)
    
    expect(screen.getByText('Live Race Tracker')).toBeInTheDocument()
    expect(screen.getByText('Race - Bahrain')).toBeInTheDocument()
    expect(screen.getByTestId('session-mode-indicator')).toBeInTheDocument()
    expect(screen.getByTestId('position-tracker')).toBeInTheDocument()
    expect(screen.getByTestId('interval-display')).toBeInTheDocument()
    expect(screen.getByTestId('weather-widget')).toBeInTheDocument()
    expect(screen.getByTestId('race-control-feed')).toBeInTheDocument()
  })

  it('displays circuit information in header', () => {
    vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
      sessionInfo: {
        session_key: '9158',
        session_name: 'Race',
        session_type: 'Race',
        date_start: new Date().toISOString(),
        date_end: new Date().toISOString(),
        gmt_offset: '+00:00',
        location: 'Bahrain',
        country_name: 'Bahrain',
        circuit_short_name: 'Bahrain International Circuit',
        mode: 'live',
      },
      sessionMode: 'live',
      isLoading: false,
      sessionError: null,
      refetchSession: vi.fn(),
      wsStatus: 'connected',
      isLoadingInitialData: false,
    })

    renderWithClient(<LiveTrackerPage />)
    
    expect(screen.getByText('Race - Bahrain')).toBeInTheDocument()
    expect(screen.getByText('Bahrain International Circuit • Bahrain')).toBeInTheDocument()
  })
})
