import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PitStopList } from '../../components/live/PitStopList'
import { useLiveRaceStore } from '../../store/liveRaceStore'
import type { PitStop, Driver } from '../../types/live'

describe('PitStopList', () => {
  beforeEach(() => {
    // Clear store before each test
    useLiveRaceStore.setState({
      pitStops: [],
      drivers: []
    })
  })
  
  it('should display "No pit stops recorded" when there are no pit stops', () => {
    render(<PitStopList />)
    expect(screen.getByText('No pit stops recorded')).toBeInTheDocument()
  })
  
  it('should display total pit stops count in header', () => {
    const drivers: Driver[] = [
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
      }
    ]
    
    const pitStops: PitStop[] = [
      {
        driver_number: 1,
        lap_number: 15,
        stop_duration: 22.5,
        lane_duration: 18.2,
        date: '2024-01-15T14:30:00Z'
      },
      {
        driver_number: 44,
        lap_number: 18,
        stop_duration: 24.8,
        lane_duration: 20.1,
        date: '2024-01-15T14:35:00Z'
      }
    ]
    
    useLiveRaceStore.setState({ pitStops, drivers })
    
    render(<PitStopList />)
    expect(screen.getByText('Total: 2')).toBeInTheDocument()
  })
  
  it('should highlight fastest pit stop with green background', () => {
    const drivers: Driver[] = [
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
      }
    ]
    
    const pitStops: PitStop[] = [
      {
        driver_number: 1,
        lap_number: 15,
        stop_duration: 20.5, // Fastest
        lane_duration: 18.2,
        date: '2024-01-15T14:30:00Z'
      },
      {
        driver_number: 44,
        lap_number: 18,
        stop_duration: 24.8,
        lane_duration: 20.1,
        date: '2024-01-15T14:35:00Z'
      }
    ]
    
    useLiveRaceStore.setState({ pitStops, drivers })
    
    const { container } = render(<PitStopList />)
    
    // Find the fastest pit stop row (should have bg-green-50)
    const fastestRow = container.querySelector('.bg-green-50')
    expect(fastestRow).toBeInTheDocument()
    expect(fastestRow?.textContent).toContain('M. VERSTAPPEN')
    expect(fastestRow?.textContent).toContain('#1')
  })
  
  it('should highlight slowest pit stop with red background', () => {
    const drivers: Driver[] = [
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
      }
    ]
    
    const pitStops: PitStop[] = [
      {
        driver_number: 1,
        lap_number: 15,
        stop_duration: 20.5,
        lane_duration: 18.2,
        date: '2024-01-15T14:30:00Z'
      },
      {
        driver_number: 44,
        lap_number: 18,
        stop_duration: 28.8, // Slowest
        lane_duration: 20.1,
        date: '2024-01-15T14:35:00Z'
      }
    ]
    
    useLiveRaceStore.setState({ pitStops, drivers })
    
    const { container } = render(<PitStopList />)
    
    // Find the slowest pit stop row (should have bg-red-50)
    const slowestRow = container.querySelector('.bg-red-50')
    expect(slowestRow).toBeInTheDocument()
    expect(slowestRow?.textContent).toContain('L. HAMILTON')
    expect(slowestRow?.textContent).toContain('#2')
  })
  
  it('should display pit stops in chronological order (most recent first)', () => {
    const drivers: Driver[] = [
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
    
    const pitStops: PitStop[] = [
      {
        driver_number: 1,
        lap_number: 15,
        stop_duration: 22.5,
        lane_duration: 18.2,
        date: '2024-01-15T14:30:00Z' // Oldest
      },
      {
        driver_number: 44,
        lap_number: 18,
        stop_duration: 24.8,
        lane_duration: 20.1,
        date: '2024-01-15T14:35:00Z' // Middle
      },
      {
        driver_number: 16,
        lap_number: 20,
        stop_duration: 21.2,
        lane_duration: 17.8,
        date: '2024-01-15T14:40:00Z' // Most recent
      }
    ]
    
    useLiveRaceStore.setState({ pitStops, drivers })
    
    const { container } = render(<PitStopList />)
    
    // Get all pit stop rows
    const rows = container.querySelectorAll('.border-b')
    
    // First row should be most recent (Leclerc)
    expect(rows[0].textContent).toContain('C. LECLERC')
    
    // Second row should be middle (Hamilton)
    expect(rows[1].textContent).toContain('L. HAMILTON')
    
    // Third row should be oldest (Verstappen)
    expect(rows[2].textContent).toContain('M. VERSTAPPEN')
  })
  
  it('should exclude pit stops with null duration from ranking', () => {
    const drivers: Driver[] = [
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
      }
    ]
    
    const pitStops: PitStop[] = [
      {
        driver_number: 1,
        lap_number: 15,
        stop_duration: 22.5,
        lane_duration: 18.2,
        date: '2024-01-15T14:30:00Z'
      },
      {
        driver_number: 44,
        lap_number: 18,
        stop_duration: null, // No duration data
        lane_duration: 20.1,
        date: '2024-01-15T14:35:00Z'
      }
    ]
    
    useLiveRaceStore.setState({ pitStops, drivers })
    
    render(<PitStopList />)
    
    // Should only show 1 pit stop (the one with valid duration)
    expect(screen.getByText('Total: 1')).toBeInTheDocument()
    expect(screen.getByText('M. VERSTAPPEN')).toBeInTheDocument()
    expect(screen.queryByText('L. HAMILTON')).not.toBeInTheDocument()
  })
})
