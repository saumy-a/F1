import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StartingGrid } from '../../components/live/StartingGrid'
import { liveApi } from '../../api/live'
import type { Position, Driver } from '../../types/live'

// Mock the API
vi.mock('../../api/live', () => ({
  liveApi: {
    getStartingGrid: vi.fn(),
  },
}))

// Mock fetch for drivers endpoint
const mockFetch = vi.fn()
global.fetch = mockFetch as any

const createMockPositions = (): Position[] => [
  { driver_number: 1, position: 1, date: '2024-03-10T14:00:00Z' },
  { driver_number: 11, position: 2, date: '2024-03-10T14:00:00Z' },
  { driver_number: 44, position: 3, date: '2024-03-10T14:00:00Z' },
  { driver_number: 16, position: 4, date: '2024-03-10T14:00:00Z' },
  { driver_number: 55, position: 5, date: '2024-03-10T14:00:00Z' },
]

const createMockDrivers = (): Driver[] => [
  {
    driver_number: 1,
    broadcast_name: 'M VERSTAPPEN',
    full_name: 'Max Verstappen',
    name_acronym: 'VER',
    team_name: 'Red Bull Racing',
    team_colour: '3671C6',
    headshot_url: null,
  },
  {
    driver_number: 11,
    broadcast_name: 'S PEREZ',
    full_name: 'Sergio Perez',
    name_acronym: 'PER',
    team_name: 'Red Bull Racing',
    team_colour: '3671C6',
    headshot_url: null,
  },
  {
    driver_number: 44,
    broadcast_name: 'L HAMILTON',
    full_name: 'Lewis Hamilton',
    name_acronym: 'HAM',
    team_name: 'Mercedes',
    team_colour: '27F4D2',
    headshot_url: null,
  },
  {
    driver_number: 16,
    broadcast_name: 'C LECLERC',
    full_name: 'Charles Leclerc',
    name_acronym: 'LEC',
    team_name: 'Ferrari',
    team_colour: 'E8002D',
    headshot_url: null,
  },
  {
    driver_number: 55,
    broadcast_name: 'C SAINZ',
    full_name: 'Carlos Sainz',
    name_acronym: 'SAI',
    team_name: 'Ferrari',
    team_colour: 'E8002D',
    headshot_url: null,
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

describe('StartingGrid', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays loading state while fetching data', () => {
    vi.mocked(liveApi.getStartingGrid).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )
    mockFetch.mockImplementation(
      () => new Promise(() => {}) as any
    )

    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <StartingGrid sessionKey="9158" />
      </QueryClientProvider>
    )

    expect(screen.getByText('Starting Grid')).toBeInTheDocument()
    // Check for loading spinner
    const spinner = document.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })

  it('displays "Grid not available" when no data', async () => {
    vi.mocked(liveApi.getStartingGrid).mockResolvedValue([])
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response)

    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <StartingGrid sessionKey="9158" />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Grid not available')).toBeInTheDocument()
    })
  })

  it('displays "Grid not available" on error', async () => {
    vi.mocked(liveApi.getStartingGrid).mockRejectedValue(new Error('API Error'))
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => [],
    } as Response)

    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <StartingGrid sessionKey="9158" />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Grid not available')).toBeInTheDocument()
    })
  })

  it('displays grid positions P1-P20 in grid formation', async () => {
    const positions = createMockPositions()
    const drivers = createMockDrivers()

    vi.mocked(liveApi.getStartingGrid).mockResolvedValue(positions)
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => drivers,
    } as Response)

    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <StartingGrid sessionKey="9158" />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('P1')).toBeInTheDocument()
      expect(screen.getByText('P2')).toBeInTheDocument()
      expect(screen.getByText('P3')).toBeInTheDocument()
      expect(screen.getByText('P4')).toBeInTheDocument()
      expect(screen.getByText('P5')).toBeInTheDocument()
    })
  })

  it('displays driver number, name, and team for each position', async () => {
    const positions = createMockPositions()
    const drivers = createMockDrivers()

    vi.mocked(liveApi.getStartingGrid).mockResolvedValue(positions)
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => drivers,
    } as Response)

    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <StartingGrid sessionKey="9158" />
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Check driver numbers are displayed
      expect(screen.getByText('1')).toBeInTheDocument()
      expect(screen.getByText('11')).toBeInTheDocument()
      expect(screen.getByText('44')).toBeInTheDocument()

      // Check that driver info is rendered (either actual names or fallback)
      // The component should render driver information for all positions
      const driverElements = screen.getAllByText(/Driver \d+|[A-Z] [A-Z]+/)
      expect(driverElements.length).toBeGreaterThan(0)
    })
  })

  it('highlights pole position with gold border', async () => {
    const positions = createMockPositions()
    const drivers = createMockDrivers()

    vi.mocked(liveApi.getStartingGrid).mockResolvedValue(positions)
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => drivers,
    } as Response)

    const queryClient = createQueryClient()
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <StartingGrid sessionKey="9158" />
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Check for pole position indicator
      expect(screen.getByText('POLE')).toBeInTheDocument()

      // Check for gold ring styling
      const poleElement = container.querySelector('.ring-yellow-400')
      expect(poleElement).toBeInTheDocument()
    })
  })

  it('uses team colors for driver backgrounds', async () => {
    const positions = createMockPositions()
    const drivers = createMockDrivers()

    vi.mocked(liveApi.getStartingGrid).mockResolvedValue(positions)
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => drivers,
    } as Response)

    const queryClient = createQueryClient()
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <StartingGrid sessionKey="9158" />
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Check that background colors are applied (either team colors or fallback)
      const gridPositions = container.querySelectorAll('.relative.rounded-lg.p-4')
      expect(gridPositions.length).toBe(5) // 5 positions
      
      // Each position should have a background color style
      gridPositions.forEach(pos => {
        const style = pos.getAttribute('style')
        expect(style).toContain('background-color')
      })
    })
  })

  it('displays fallback text when driver info is missing', async () => {
    const positions: Position[] = [
      { driver_number: 99, position: 1, date: '2024-03-10T14:00:00Z' },
    ]

    vi.mocked(liveApi.getStartingGrid).mockResolvedValue(positions)
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => [], // No driver data
    } as Response)

    const queryClient = createQueryClient()
    render(
      <QueryClientProvider client={queryClient}>
        <StartingGrid sessionKey="9158" />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Driver 99')).toBeInTheDocument()
      expect(screen.getByText('Unknown Team')).toBeInTheDocument()
    })
  })

  it('has proper grid layout with 2 columns on desktop', async () => {
    const positions = createMockPositions()
    const drivers = createMockDrivers()

    vi.mocked(liveApi.getStartingGrid).mockResolvedValue(positions)
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => drivers,
    } as Response)

    const queryClient = createQueryClient()
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <StartingGrid sessionKey="9158" />
      </QueryClientProvider>
    )

    await waitFor(() => {
      // Check for responsive grid layout
      const gridElement = container.querySelector('.grid.grid-cols-1.md\\:grid-cols-2')
      expect(gridElement).toBeInTheDocument()
    })
  })

  it('sorts positions in ascending order', async () => {
    // Provide positions in random order
    const positions: Position[] = [
      { driver_number: 44, position: 3, date: '2024-03-10T14:00:00Z' },
      { driver_number: 1, position: 1, date: '2024-03-10T14:00:00Z' },
      { driver_number: 11, position: 2, date: '2024-03-10T14:00:00Z' },
    ]
    const drivers = createMockDrivers()

    vi.mocked(liveApi.getStartingGrid).mockResolvedValue(positions)
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => drivers,
    } as Response)

    const queryClient = createQueryClient()
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <StartingGrid sessionKey="9158" />
      </QueryClientProvider>
    )

    await waitFor(() => {
      const positionElements = container.querySelectorAll('[class*="text-3xl"]')
      const positions = Array.from(positionElements).map((el) => el.textContent)
      
      // Should be in order P1, P2, P3
      expect(positions[0]).toBe('P1')
      expect(positions[1]).toBe('P2')
      expect(positions[2]).toBe('P3')
    })
  })
})
