import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { CircuitInfo } from '../../components/live/CircuitInfo'
import type { SessionInfo } from '../../types/live'

const createMockSession = (overrides?: Partial<SessionInfo>): SessionInfo => ({
  session_key: '9158',
  session_name: 'Race',
  session_type: 'Race',
  date_start: '2024-03-10T14:00:00Z',
  date_end: '2024-03-10T16:00:00Z',
  gmt_offset: '+03:00',
  location: 'Sakhir',
  country_name: 'Bahrain',
  circuit_short_name: 'Bahrain International Circuit',
  mode: 'upcoming',
  ...overrides,
})

describe('CircuitInfo', () => {
  it('displays circuit name', () => {
    const sessionInfo = createMockSession()
    render(<CircuitInfo sessionInfo={sessionInfo} />)
    
    expect(screen.getByText('Bahrain International Circuit')).toBeInTheDocument()
  })

  it('displays circuit location with city and country', () => {
    const sessionInfo = createMockSession()
    render(<CircuitInfo sessionInfo={sessionInfo} />)
    
    expect(screen.getByText('Sakhir, Bahrain')).toBeInTheDocument()
  })

  it('displays Circuit Information heading', () => {
    const sessionInfo = createMockSession()
    render(<CircuitInfo sessionInfo={sessionInfo} />)
    
    expect(screen.getByText('Circuit Information')).toBeInTheDocument()
  })

  it('displays circuit image placeholder', () => {
    const sessionInfo = createMockSession()
    render(<CircuitInfo sessionInfo={sessionInfo} />)
    
    expect(screen.getByText('Circuit map not available')).toBeInTheDocument()
  })

  it('displays circuit detail labels', () => {
    const sessionInfo = createMockSession()
    render(<CircuitInfo sessionInfo={sessionInfo} />)
    
    expect(screen.getByText('Circuit Length')).toBeInTheDocument()
    expect(screen.getByText('Number of Laps')).toBeInTheDocument()
    expect(screen.getByText('Race Distance')).toBeInTheDocument()
    expect(screen.getByText('DRS Zones')).toBeInTheDocument()
  })

  it('displays N/A for unavailable circuit details', () => {
    const sessionInfo = createMockSession()
    render(<CircuitInfo sessionInfo={sessionInfo} />)
    
    // All detail values should be N/A since data is not available
    const naElements = screen.getAllByText('N/A')
    expect(naElements.length).toBeGreaterThanOrEqual(4)
  })

  it('displays lap record section', () => {
    const sessionInfo = createMockSession()
    render(<CircuitInfo sessionInfo={sessionInfo} />)
    
    expect(screen.getByText('Lap Record')).toBeInTheDocument()
    expect(screen.getByText('Lap record data not available')).toBeInTheDocument()
  })

  it('renders different circuit names correctly', () => {
    const sessionInfo = createMockSession({
      circuit_short_name: 'Monaco',
      location: 'Monte Carlo',
      country_name: 'Monaco'
    })
    render(<CircuitInfo sessionInfo={sessionInfo} />)
    
    expect(screen.getByText('Monaco')).toBeInTheDocument()
    expect(screen.getByText('Monte Carlo, Monaco')).toBeInTheDocument()
  })

  it('has proper grid layout for circuit details', () => {
    const sessionInfo = createMockSession()
    const { container } = render(<CircuitInfo sessionInfo={sessionInfo} />)
    
    // Check for grid layout
    const gridElement = container.querySelector('.grid.grid-cols-2')
    expect(gridElement).toBeInTheDocument()
  })

  it('displays circuit details in rounded boxes', () => {
    const sessionInfo = createMockSession()
    const { container } = render(<CircuitInfo sessionInfo={sessionInfo} />)
    
    // Check for rounded styling on detail boxes
    const detailBoxes = container.querySelectorAll('.bg-gray-50.rounded-lg')
    expect(detailBoxes.length).toBeGreaterThan(0)
  })
})
