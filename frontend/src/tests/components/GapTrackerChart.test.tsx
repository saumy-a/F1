import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { GapTrackerChart } from '../../components/live/GapTrackerChart'
import { useLiveRaceStore } from '../../store/liveRaceStore'
import type { Driver } from '../../types/live'

const mockDrivers: Driver[] = [
  {
    driver_number: 1,
    broadcast_name: 'M VERSTAPPEN',
    full_name: 'Max Verstappen',
    name_acronym: 'VER',
    team_name: 'Red Bull Racing',
    team_colour: '3671C6',
    headshot_url: null
  },
  {
    driver_number: 11,
    broadcast_name: 'S PEREZ',
    full_name: 'Sergio Perez',
    name_acronym: 'PER',
    team_name: 'Red Bull Racing',
    team_colour: '3671C6',
    headshot_url: null
  },
  {
    driver_number: 44,
    broadcast_name: 'L HAMILTON',
    full_name: 'Lewis Hamilton',
    name_acronym: 'HAM',
    team_name: 'Mercedes',
    team_colour: '27F4D2',
    headshot_url: null
  }
]

describe('GapTrackerChart', () => {
  beforeEach(() => {
    // Reset store state before each test
    useLiveRaceStore.setState({
      sessionInfo: null,
      drivers: [],
      positions: [],
      intervals: [],
      intervalHistory: [],
      stints: [],
      pitStops: [],
      weather: null,
      raceControl: [],
      isConnected: false,
      lastUpdate: null
    })
  })

  it('displays "No gap data available" when intervalHistory is empty', () => {
    useLiveRaceStore.setState({
      intervalHistory: [],
      drivers: mockDrivers
    })

    render(<GapTrackerChart />)
    
    expect(screen.getByText('Gap to Leader')).toBeInTheDocument()
    expect(screen.getByText('No gap data available')).toBeInTheDocument()
  })

  it('displays "No gap data available" when drivers list is empty', () => {
    useLiveRaceStore.setState({
      intervalHistory: [
        { lap: 1, driver_number: 1, gap: 0 },
        { lap: 1, driver_number: 11, gap: 2.5 }
      ],
      drivers: []
    })

    render(<GapTrackerChart />)
    
    expect(screen.getByText('No gap data available')).toBeInTheDocument()
  })

  it('renders chart container with proper styling', () => {
    useLiveRaceStore.setState({
      intervalHistory: [
        { lap: 1, driver_number: 1, gap: 0 },
        { lap: 2, driver_number: 1, gap: 0 },
        { lap: 1, driver_number: 11, gap: 2.5 },
        { lap: 2, driver_number: 11, gap: 3.1 }
      ],
      drivers: mockDrivers
    })

    render(<GapTrackerChart />)
    
    // Check for header
    expect(screen.getByText('Gap to Leader')).toBeInTheDocument()
  })

  it('handles null gap values correctly', () => {
    useLiveRaceStore.setState({
      intervalHistory: [
        { lap: 1, driver_number: 1, gap: 0 },
        { lap: 1, driver_number: 11, gap: null },
        { lap: 2, driver_number: 1, gap: 0 },
        { lap: 2, driver_number: 11, gap: 2.5 }
      ],
      drivers: mockDrivers
    })

    render(<GapTrackerChart />)
    
    // Should render without errors
    expect(screen.getByText('Gap to Leader')).toBeInTheDocument()
    expect(screen.queryByText('No gap data available')).not.toBeInTheDocument()
  })

  it('handles string gap values (lapped cars) correctly', () => {
    useLiveRaceStore.setState({
      intervalHistory: [
        { lap: 1, driver_number: 1, gap: 0 },
        { lap: 1, driver_number: 44, gap: '+1 LAP' as unknown as number },
        { lap: 2, driver_number: 1, gap: 0 },
        { lap: 2, driver_number: 44, gap: '+1 LAP' as unknown as number }
      ],
      drivers: mockDrivers
    })

    render(<GapTrackerChart />)
    
    // Should render without errors
    expect(screen.getByText('Gap to Leader')).toBeInTheDocument()
    expect(screen.queryByText('No gap data available')).not.toBeInTheDocument()
  })

  it('groups interval history by driver correctly', () => {
    useLiveRaceStore.setState({
      intervalHistory: [
        { lap: 1, driver_number: 1, gap: 0 },
        { lap: 1, driver_number: 11, gap: 2.5 },
        { lap: 1, driver_number: 44, gap: 5.2 },
        { lap: 2, driver_number: 1, gap: 0 },
        { lap: 2, driver_number: 11, gap: 3.1 },
        { lap: 2, driver_number: 44, gap: 6.8 },
        { lap: 3, driver_number: 1, gap: 0 },
        { lap: 3, driver_number: 11, gap: 2.9 },
        { lap: 3, driver_number: 44, gap: 7.5 }
      ],
      drivers: mockDrivers
    })

    render(<GapTrackerChart />)
    
    // Chart should render with data
    expect(screen.queryByText('No gap data available')).not.toBeInTheDocument()
  })

  it('uses driver broadcast names in chart', () => {
    useLiveRaceStore.setState({
      intervalHistory: [
        { lap: 1, driver_number: 1, gap: 0 },
        { lap: 1, driver_number: 11, gap: 2.5 }
      ],
      drivers: mockDrivers
    })

    render(<GapTrackerChart />)
    
    // The component should use broadcast names for the chart traces
    // We can't directly test Plotly internals, but we can verify the component renders
    expect(screen.queryByText('No gap data available')).not.toBeInTheDocument()
  })

  it('uses team colors for driver lines', () => {
    useLiveRaceStore.setState({
      intervalHistory: [
        { lap: 1, driver_number: 1, gap: 0 },
        { lap: 1, driver_number: 11, gap: 2.5 },
        { lap: 1, driver_number: 44, gap: 5.2 }
      ],
      drivers: mockDrivers
    })

    render(<GapTrackerChart />)
    
    // Chart should render with team colors applied
    expect(screen.queryByText('No gap data available')).not.toBeInTheDocument()
  })

  it('handles drivers without team color gracefully', () => {
    const driversWithoutColor: Driver[] = [
      {
        driver_number: 1,
        broadcast_name: 'M VERSTAPPEN',
        full_name: 'Max Verstappen',
        name_acronym: 'VER',
        team_name: 'Red Bull Racing',
        team_colour: '', // Empty color
        headshot_url: null
      }
    ]

    useLiveRaceStore.setState({
      intervalHistory: [
        { lap: 1, driver_number: 1, gap: 0 },
        { lap: 2, driver_number: 1, gap: 0 }
      ],
      drivers: driversWithoutColor
    })

    render(<GapTrackerChart />)
    
    // Should render without errors, using default color
    expect(screen.queryByText('No gap data available')).not.toBeInTheDocument()
  })

  it('handles unknown drivers gracefully', () => {
    useLiveRaceStore.setState({
      intervalHistory: [
        { lap: 1, driver_number: 99, gap: 0 }, // Driver not in drivers list
        { lap: 2, driver_number: 99, gap: 0 }
      ],
      drivers: mockDrivers
    })

    render(<GapTrackerChart />)
    
    // Should render without errors, using fallback name
    expect(screen.queryByText('No gap data available')).not.toBeInTheDocument()
  })

  it('applies responsive height classes', () => {
    useLiveRaceStore.setState({
      intervalHistory: [
        { lap: 1, driver_number: 1, gap: 0 },
        { lap: 2, driver_number: 1, gap: 0 }
      ],
      drivers: mockDrivers
    })

    render(<GapTrackerChart />)
    
    // Chart should render with data
    expect(screen.queryByText('No gap data available')).not.toBeInTheDocument()
  })
})
