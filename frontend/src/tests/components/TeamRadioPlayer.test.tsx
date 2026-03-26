import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { TeamRadioPlayer } from '../../components/live/TeamRadioPlayer'
import { useLiveRaceStore } from '../../store/liveRaceStore'
import { liveApi } from '../../api/live'
import type { TeamRadio, Driver, SessionInfo } from '../../types/live'

// Mock the API
vi.mock('../../api/live', () => ({
  liveApi: {
    getTeamRadio: vi.fn()
  }
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('TeamRadioPlayer', () => {
  const mockDrivers: Driver[] = [
    {
      driver_number: 1,
      broadcast_name: 'M. VERSTAPPEN',
      full_name: 'Max Verstappen',
      name_acronym: 'VER',
      team_name: 'Red Bull Racing',
      team_colour: '3671C6',
      headshot_url: null
    },
    {
      driver_number: 44,
      broadcast_name: 'L. HAMILTON',
      full_name: 'Lewis Hamilton',
      name_acronym: 'HAM',
      team_name: 'Mercedes',
      team_colour: '27F4D2',
      headshot_url: null
    },
    {
      driver_number: 16,
      broadcast_name: 'C. LECLERC',
      full_name: 'Charles Leclerc',
      name_acronym: 'LEC',
      team_name: 'Ferrari',
      team_colour: 'E8002D',
      headshot_url: null
    }
  ]

  const mockSessionInfo: SessionInfo = {
    session_key: '9158',
    session_name: 'Race',
    session_type: 'Race',
    date_start: '2024-03-10T14:00:00Z',
    date_end: '2024-03-10T16:00:00Z',
    gmt_offset: '+01:00',
    location: 'Bahrain',
    country_name: 'Bahrain',
    circuit_short_name: 'Bahrain',
    mode: 'replay'
  }

  const mockRadioClips: TeamRadio[] = [
    {
      driver_number: 1,
      date: '2024-03-10T14:30:00Z',
      recording_url: 'https://example.com/radio1.mp3',
      duration: 5.2
    },
    {
      driver_number: 44,
      date: '2024-03-10T14:35:00Z',
      recording_url: 'https://example.com/radio2.mp3',
      duration: 3.8
    },
    {
      driver_number: 16,
      date: '2024-03-10T14:40:00Z',
      recording_url: 'https://example.com/radio3.mp3',
      duration: 7.1
    }
  ]

  beforeEach(() => {
    // Clear store before each test
    useLiveRaceStore.setState({
      sessionInfo: null,
      drivers: []
    })
    
    // Reset mocks
    vi.clearAllMocks()
  })

  it('should display loading state while fetching radio clips', () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockImplementation(() => new Promise(() => {}))
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    expect(screen.getByText('Loading radio clips...')).toBeInTheDocument()
  })

  it('should display "No radio clips available" when there are no clips', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue([])
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('No radio clips available')).toBeInTheDocument()
    })
  })

  it('should display error message when API call fails', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockRejectedValue(new Error('API Error'))
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('Failed to load radio clips')).toBeInTheDocument()
    })
  })

  it('should display list of radio clips with driver names and timestamps', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue(mockRadioClips)
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('M. VERSTAPPEN')).toBeInTheDocument()
      expect(screen.getByText('L. HAMILTON')).toBeInTheDocument()
      expect(screen.getByText('C. LECLERC')).toBeInTheDocument()
    })
  })

  it('should display total clips count in header', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue(mockRadioClips)
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('3 clips')).toBeInTheDocument()
    })
  })

  it('should display clips in reverse chronological order by default', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue(mockRadioClips)
    
    const { container } = render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      const clips = container.querySelectorAll('.border-gray-200.rounded-lg')
      
      // Most recent clip (Leclerc) should be first
      expect(clips[0].textContent).toContain('C. LECLERC')
      
      // Middle clip (Hamilton) should be second
      expect(clips[1].textContent).toContain('L. HAMILTON')
      
      // Oldest clip (Verstappen) should be last
      expect(clips[2].textContent).toContain('M. VERSTAPPEN')
    })
  })

  it('should filter clips by selected driver', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue(mockRadioClips)
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('M. VERSTAPPEN')).toBeInTheDocument()
    })
    
    // Select driver filter
    const filterSelect = screen.getByLabelText('Filter by Driver')
    fireEvent.change(filterSelect, { target: { value: '1' } })
    
    await waitFor(() => {
      expect(screen.getByText('M. VERSTAPPEN')).toBeInTheDocument()
      expect(screen.queryByText('L. HAMILTON')).not.toBeInTheDocument()
      expect(screen.queryByText('C. LECLERC')).not.toBeInTheDocument()
    })
  })

  it('should sort clips by driver number when sort option is changed', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue(mockRadioClips)
    
    const { container } = render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('M. VERSTAPPEN')).toBeInTheDocument()
    })
    
    // Change sort to driver number
    const sortSelect = screen.getByLabelText('Sort by')
    fireEvent.change(sortSelect, { target: { value: 'driver' } })
    
    await waitFor(() => {
      const clips = container.querySelectorAll('.border-gray-200.rounded-lg')
      
      // Should be sorted by driver number: 1, 16, 44
      expect(clips[0].textContent).toContain('M. VERSTAPPEN')
      expect(clips[1].textContent).toContain('C. LECLERC')
      expect(clips[2].textContent).toContain('L. HAMILTON')
    })
  })

  it('should display duration for each clip', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue(mockRadioClips)
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('Duration: 0:05')).toBeInTheDocument() // 5.2 seconds
      expect(screen.getByText('Duration: 0:03')).toBeInTheDocument() // 3.8 seconds
      expect(screen.getByText('Duration: 0:07')).toBeInTheDocument() // 7.1 seconds
    })
  })

  it('should display team name for each driver', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue(mockRadioClips)
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('Red Bull Racing')).toBeInTheDocument()
      expect(screen.getByText('Mercedes')).toBeInTheDocument()
      expect(screen.getByText('Ferrari')).toBeInTheDocument()
    })
  })

  it('should display play button for each clip', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue(mockRadioClips)
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      const playButtons = screen.getAllByLabelText('Play')
      expect(playButtons).toHaveLength(3)
    })
  })

  it('should show "No clips match the selected filter" when filter returns no results', async () => {
    // Add a driver with no radio clips
    const driversWithExtra: Driver[] = [
      ...mockDrivers,
      {
        driver_number: 99,
        broadcast_name: 'TEST DRIVER',
        full_name: 'Test Driver',
        name_acronym: 'TST',
        team_name: 'Test Team',
        team_colour: '000000',
        headshot_url: null
      }
    ]
    
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: driversWithExtra
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue(mockRadioClips)
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('M. VERSTAPPEN')).toBeInTheDocument()
    })
    
    // Select a driver that has no clips
    const filterSelect = screen.getByLabelText('Filter by Driver')
    fireEvent.change(filterSelect, { target: { value: '99' } })
    
    await waitFor(() => {
      expect(screen.getByText('No clips match the selected filter')).toBeInTheDocument()
    })
  })

  it('should display driver number when driver info is not available', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: [] // No driver info
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue([mockRadioClips[0]])
    
    render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      expect(screen.getByText('Driver #1')).toBeInTheDocument()
    })
  })

  it('should use team color for clip border', async () => {
    useLiveRaceStore.setState({
      sessionInfo: mockSessionInfo,
      drivers: mockDrivers
    })
    
    vi.mocked(liveApi.getTeamRadio).mockResolvedValue([mockRadioClips[0]])
    
    const { container } = render(<TeamRadioPlayer />, { wrapper: createWrapper() })
    
    await waitFor(() => {
      const clipElement = container.querySelector('.border-gray-200.rounded-lg')
      expect(clipElement).toHaveStyle({ borderLeftColor: '#3671C6' })
    })
  })
})

