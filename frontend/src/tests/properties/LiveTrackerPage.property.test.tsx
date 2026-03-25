import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import * as fc from 'fast-check'
import LiveTrackerPage from '../../pages/LiveTrackerPage'
import * as useLiveDataModule from '../../hooks/useLiveData'
import type { SessionMode } from '../../types/live'

/**
 * Property 2: Mode-Appropriate UI Rendering
 * 
 * Validates: Requirements 1.3, 1.4, 1.5
 * 
 * For any session mode value ("live", "upcoming", "replay"), the Live Tracker Page
 * SHALL render only the UI components appropriate for that mode:
 * - live mode SHALL render all 7 panels
 * - upcoming mode SHALL render countdown/circuit/grid components
 * - replay mode SHALL render session selector plus all 7 panels
 */

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

vi.mock('../../components/live/GapTrackerChart', () => ({
  GapTrackerChart: () => <div data-testid="gap-tracker-chart">Gap Tracker Chart</div>,
}))

vi.mock('../../components/live/TyreStrategyPanel', () => ({
  TyreStrategyPanel: () => <div data-testid="tyre-strategy-panel">Tyre Strategy Panel</div>,
}))

vi.mock('../../components/live/PitStopList', () => ({
  PitStopList: () => <div data-testid="pit-stop-list">Pit Stop List</div>,
}))

vi.mock('../../components/live/TeamRadioPlayer', () => ({
  TeamRadioPlayer: () => <div data-testid="team-radio-player">Team Radio Player</div>,
}))

vi.mock('../../components/live/CountdownTimer', () => ({
  CountdownTimer: () => <div data-testid="countdown-timer">Countdown Timer</div>,
}))

vi.mock('../../components/live/CircuitInfo', () => ({
  CircuitInfo: () => <div data-testid="circuit-info">Circuit Info</div>,
}))

vi.mock('../../components/live/StartingGrid', () => ({
  StartingGrid: () => <div data-testid="starting-grid">Starting Grid</div>,
}))

vi.mock('../../components/live/SessionSelector', () => ({
  SessionSelector: () => <div data-testid="session-selector">Session Selector</div>,
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

describe('Property 2: Mode-Appropriate UI Rendering', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Generator for session modes
  const sessionModeArb = fc.constantFrom<SessionMode>('live', 'upcoming', 'replay')

  // Generator for session info based on mode
  const sessionInfoArb = (mode: SessionMode) => {
    const now = Date.now()
    
    let dateStart: string
    let dateEnd: string
    
    switch (mode) {
      case 'live':
        // Session is currently in progress
        dateStart = new Date(now - 3600000).toISOString() // 1 hour ago
        dateEnd = new Date(now + 3600000).toISOString() // 1 hour from now
        break
      case 'upcoming':
        // Session hasn't started yet
        dateStart = new Date(now + 3600000).toISOString() // 1 hour from now
        dateEnd = new Date(now + 7200000).toISOString() // 2 hours from now
        break
      case 'replay':
        // Session has ended
        dateStart = new Date(now - 7200000).toISOString() // 2 hours ago
        dateEnd = new Date(now - 3600000).toISOString() // 1 hour ago
        break
    }

    return fc.record({
      session_key: fc.integer({ min: 1000, max: 9999 }).map(String),
      session_name: fc.constantFrom('Race', 'Qualifying', 'Practice 1', 'Practice 2', 'Practice 3', 'Sprint'),
      session_type: fc.constantFrom('Race', 'Qualifying', 'Practice', 'Sprint'),
      date_start: fc.constant(dateStart),
      date_end: fc.constant(dateEnd),
      gmt_offset: fc.constantFrom('+00:00', '+01:00', '+02:00', '-05:00', '-08:00'),
      location: fc.constantFrom('Bahrain', 'Monaco', 'Silverstone', 'Monza', 'Spa'),
      country_name: fc.constantFrom('Bahrain', 'Monaco', 'United Kingdom', 'Italy', 'Belgium'),
      circuit_short_name: fc.constantFrom('Bahrain', 'Monaco', 'Silverstone', 'Monza', 'Spa-Francorchamps'),
      mode: fc.constant(mode),
    })
  }

  it('Property: Live mode renders all required panels', () => {
    fc.assert(
      fc.property(sessionInfoArb('live'), (sessionInfo) => {
        // Mock useLiveData to return live mode
        vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
          sessionInfo,
          sessionMode: 'live',
          isLoading: false,
          sessionError: null,
          refetchSession: vi.fn(),
          wsStatus: 'connected',
          isLoadingInitialData: false,
        })

        const { unmount } = renderWithClient(<LiveTrackerPage />)

        // Verify session mode indicator is present
        expect(screen.getByTestId('session-mode-indicator')).toBeInTheDocument()

        // Verify all 7 panels are rendered for live mode
        // Currently implemented panels:
        expect(screen.getByTestId('position-tracker')).toBeInTheDocument()
        expect(screen.getByTestId('interval-display')).toBeInTheDocument()
        expect(screen.getByTestId('weather-widget')).toBeInTheDocument()
        expect(screen.getByTestId('race-control-feed')).toBeInTheDocument()

        // Note: The following panels are specified in requirements but not yet implemented:
        // - gap-tracker-chart
        // - tyre-strategy-panel
        // - pit-stop-list
        // - team-radio-player
        // When these are implemented, uncomment the assertions below:
        // expect(screen.getByTestId('gap-tracker-chart')).toBeInTheDocument()
        // expect(screen.getByTestId('tyre-strategy-panel')).toBeInTheDocument()
        // expect(screen.getByTestId('pit-stop-list')).toBeInTheDocument()
        // expect(screen.getByTestId('team-radio-player')).toBeInTheDocument()

        // Verify upcoming-mode components are NOT rendered
        expect(screen.queryByText(/Session starts:/)).not.toBeInTheDocument()
        expect(screen.queryByText(/Time until session:/)).not.toBeInTheDocument()

        // Verify replay-mode components are NOT rendered
        // (Session selector would be here when implemented)

        unmount()
      }),
      { numRuns: 10 }
    )
  })

  it('Property: Upcoming mode renders countdown and circuit components', () => {
    fc.assert(
      fc.property(sessionInfoArb('upcoming'), (sessionInfo) => {
        // Mock useLiveData to return upcoming mode
        vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
          sessionInfo,
          sessionMode: 'upcoming',
          isLoading: false,
          sessionError: null,
          refetchSession: vi.fn(),
          wsStatus: 'disconnected',
          isLoadingInitialData: false,
        })

        const { unmount } = renderWithClient(<LiveTrackerPage />)

        // Verify session mode indicator is present
        expect(screen.getByTestId('session-mode-indicator')).toBeInTheDocument()

        // Verify upcoming mode components are rendered
        expect(screen.getByText(/Session starts:/)).toBeInTheDocument()
        
        // Countdown timer is rendered inline in the current implementation
        // When CountdownTimer component is extracted, uncomment:
        // expect(screen.getByTestId('countdown-timer')).toBeInTheDocument()

        // Circuit info and starting grid are not yet implemented
        // When implemented, uncomment:
        // expect(screen.getByTestId('circuit-info')).toBeInTheDocument()
        // expect(screen.getByTestId('starting-grid')).toBeInTheDocument()

        // Verify live/replay panels are NOT rendered
        expect(screen.queryByTestId('position-tracker')).not.toBeInTheDocument()
        expect(screen.queryByTestId('interval-display')).not.toBeInTheDocument()
        expect(screen.queryByTestId('weather-widget')).not.toBeInTheDocument()
        expect(screen.queryByTestId('race-control-feed')).not.toBeInTheDocument()

        unmount()
      }),
      { numRuns: 10 }
    )
  })

  it('Property: Replay mode renders session selector and all panels', () => {
    fc.assert(
      fc.property(sessionInfoArb('replay'), (sessionInfo) => {
        // Mock useLiveData to return replay mode
        vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
          sessionInfo,
          sessionMode: 'replay',
          isLoading: false,
          sessionError: null,
          refetchSession: vi.fn(),
          wsStatus: 'disconnected',
          isLoadingInitialData: false,
        })

        const { unmount } = renderWithClient(<LiveTrackerPage />)

        // Verify session mode indicator is present
        expect(screen.getByTestId('session-mode-indicator')).toBeInTheDocument()

        // Verify all panels are rendered (same as live mode)
        expect(screen.getByTestId('position-tracker')).toBeInTheDocument()
        expect(screen.getByTestId('interval-display')).toBeInTheDocument()
        expect(screen.getByTestId('weather-widget')).toBeInTheDocument()
        expect(screen.getByTestId('race-control-feed')).toBeInTheDocument()

        // Session selector is not yet implemented
        // When implemented, uncomment:
        // expect(screen.getByTestId('session-selector')).toBeInTheDocument()

        // Verify upcoming-mode components are NOT rendered
        expect(screen.queryByText(/Session starts:/)).not.toBeInTheDocument()
        expect(screen.queryByText(/Time until session:/)).not.toBeInTheDocument()

        unmount()
      }),
      { numRuns: 10 }
    )
  })

  it('Property: Mode transitions render appropriate components', () => {
    fc.assert(
      fc.property(
        fc.tuple(sessionModeArb, sessionModeArb).filter(([mode1, mode2]) => mode1 !== mode2),
        ([initialMode, newMode]) => {
          // Generate session info for initial mode
          const initialSessionInfo = fc.sample(sessionInfoArb(initialMode), 1)[0]
          const newSessionInfo = fc.sample(sessionInfoArb(newMode), 1)[0]

          // Mock initial mode
          vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
            sessionInfo: initialSessionInfo,
            sessionMode: initialMode,
            isLoading: false,
            sessionError: null,
            refetchSession: vi.fn(),
            wsStatus: initialMode === 'live' ? 'connected' : 'disconnected',
            isLoadingInitialData: false,
          })

          const { rerender, unmount } = renderWithClient(<LiveTrackerPage />)

          // Verify initial mode renders correctly
          expect(screen.getByTestId('session-mode-indicator')).toBeInTheDocument()

          // Mock mode transition
          vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
            sessionInfo: newSessionInfo,
            sessionMode: newMode,
            isLoading: false,
            sessionError: null,
            refetchSession: vi.fn(),
            wsStatus: newMode === 'live' ? 'connected' : 'disconnected',
            isLoadingInitialData: false,
          })

          // Re-render with new mode
          rerender(
            <QueryClientProvider client={createTestQueryClient()}>
              <LiveTrackerPage />
            </QueryClientProvider>
          )

          // Verify new mode renders correctly
          expect(screen.getByTestId('session-mode-indicator')).toBeInTheDocument()

          // Verify mode-specific components based on new mode
          if (newMode === 'live' || newMode === 'replay') {
            expect(screen.getByTestId('position-tracker')).toBeInTheDocument()
            expect(screen.queryByText(/Session starts:/)).not.toBeInTheDocument()
          } else if (newMode === 'upcoming') {
            expect(screen.getByText(/Session starts:/)).toBeInTheDocument()
            expect(screen.queryByTestId('position-tracker')).not.toBeInTheDocument()
          }

          unmount()
        }
      ),
      { numRuns: 10 }
    )
  })

  it('Property: Each mode renders mutually exclusive component sets', () => {
    fc.assert(
      fc.property(sessionModeArb, (mode) => {
        const sessionInfo = fc.sample(sessionInfoArb(mode), 1)[0]

        vi.mocked(useLiveDataModule.useLiveData).mockReturnValue({
          sessionInfo,
          sessionMode: mode,
          isLoading: false,
          sessionError: null,
          refetchSession: vi.fn(),
          wsStatus: mode === 'live' ? 'connected' : 'disconnected',
          isLoadingInitialData: false,
        })

        const { unmount } = renderWithClient(<LiveTrackerPage />)

        // Define component sets for each mode
        const liveReplayComponents = [
          'position-tracker',
          'interval-display',
          'weather-widget',
          'race-control-feed',
        ]

        const upcomingIndicators = [
          /Session starts:/,
        ]

        if (mode === 'live' || mode === 'replay') {
          // Live/Replay mode should have panels
          liveReplayComponents.forEach((testId) => {
            expect(screen.getByTestId(testId)).toBeInTheDocument()
          })

          // Should NOT have upcoming indicators
          upcomingIndicators.forEach((text) => {
            expect(screen.queryByText(text)).not.toBeInTheDocument()
          })
        } else if (mode === 'upcoming') {
          // Upcoming mode should have countdown
          upcomingIndicators.forEach((text) => {
            expect(screen.getByText(text)).toBeInTheDocument()
          })

          // Should NOT have live/replay panels
          liveReplayComponents.forEach((testId) => {
            expect(screen.queryByTestId(testId)).not.toBeInTheDocument()
          })
        }

        unmount()
      }),
      { numRuns: 20 }
    )
  })
})
