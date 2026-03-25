import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, act } from '@testing-library/react'
import * as fc from 'fast-check'
import { RaceTower } from '../../components/live/RaceTower'
import { useLiveRaceStore } from '../../store/liveRaceStore'
import type { Position, Interval, Driver, Stint } from '../../types/live'

describe('RaceTower', () => {
  beforeEach(() => {
    // Clear store before each test
    useLiveRaceStore.setState({
      positions: [],
      intervals: [],
      drivers: [],
      stints: [],
      sessionInfo: null,
      pitStops: [],
      weather: null,
      raceControl: [],
      isConnected: false,
      lastUpdate: null,
      intervalHistory: []
    })
  })

  it('displays empty state when no data available', () => {
    render(<RaceTower />)
    expect(screen.getByText('No race data available')).toBeInTheDocument()
  })

  it('displays race positions sorted by position', () => {
    const positions: Position[] = [
      { driver_number: 1, position: 1, date: '2024-03-10T14:30:00Z' },
      { driver_number: 44, position: 2, date: '2024-03-10T14:30:00Z' },
      { driver_number: 16, position: 3, date: '2024-03-10T14:30:00Z' }
    ]

    const drivers: Driver[] = [
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
        driver_number: 44,
        broadcast_name: 'L HAMILTON',
        full_name: 'Lewis Hamilton',
        name_acronym: 'HAM',
        team_name: 'Mercedes',
        team_colour: '27F4D2',
        headshot_url: null
      },
      {
        driver_number: 16,
        broadcast_name: 'C LECLERC',
        full_name: 'Charles Leclerc',
        name_acronym: 'LEC',
        team_name: 'Ferrari',
        team_colour: 'E8002D',
        headshot_url: null
      }
    ]

    useLiveRaceStore.setState({ positions, drivers })

    render(<RaceTower />)

    expect(screen.getByText('M VERSTAPPEN')).toBeInTheDocument()
    expect(screen.getByText('L HAMILTON')).toBeInTheDocument()
    expect(screen.getByText('C LECLERC')).toBeInTheDocument()
    expect(screen.getByText('Red Bull Racing')).toBeInTheDocument()
    expect(screen.getByText('Mercedes')).toBeInTheDocument()
    expect(screen.getByText('Ferrari')).toBeInTheDocument()
  })

  it('displays gap to leader correctly', () => {
    const positions: Position[] = [
      { driver_number: 1, position: 1, date: '2024-03-10T14:30:00Z' },
      { driver_number: 44, position: 2, date: '2024-03-10T14:30:00Z' }
    ]

    const intervals: Interval[] = [
      { driver_number: 1, gap_to_leader: null, interval: null, date: '2024-03-10T14:30:00Z' },
      { driver_number: 44, gap_to_leader: 3.456, interval: 3.456, date: '2024-03-10T14:30:00Z' }
    ]

    const drivers: Driver[] = [
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
        driver_number: 44,
        broadcast_name: 'L HAMILTON',
        full_name: 'Lewis Hamilton',
        name_acronym: 'HAM',
        team_name: 'Mercedes',
        team_colour: '27F4D2',
        headshot_url: null
      }
    ]

    useLiveRaceStore.setState({ positions, intervals, drivers })

    render(<RaceTower />)

    // P1 should show "—" for gap to leader
    const rows = screen.getAllByRole('generic').filter(el => el.className.includes('flex items-center gap-4'))
    expect(rows[0]).toHaveTextContent('—')
    
    // P2 should show gap in seconds (appears twice: gap to leader and interval)
    expect(screen.getAllByText('+3.456s')).toHaveLength(2)
  })

  it('preserves "+1 LAP" format for lapped cars', () => {
    const positions: Position[] = [
      { driver_number: 1, position: 1, date: '2024-03-10T14:30:00Z' },
      { driver_number: 20, position: 20, date: '2024-03-10T14:30:00Z' }
    ]

    const intervals: Interval[] = [
      { driver_number: 1, gap_to_leader: null, interval: null, date: '2024-03-10T14:30:00Z' },
      { driver_number: 20, gap_to_leader: '+1 LAP', interval: '+1 LAP', date: '2024-03-10T14:30:00Z' }
    ]

    const drivers: Driver[] = [
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
        driver_number: 20,
        broadcast_name: 'K MAGNUSSEN',
        full_name: 'Kevin Magnussen',
        name_acronym: 'MAG',
        team_name: 'Haas F1 Team',
        team_colour: 'B6BABD',
        headshot_url: null
      }
    ]

    useLiveRaceStore.setState({ positions, intervals, drivers })

    render(<RaceTower />)

    // "+1 LAP" appears twice: gap to leader and interval
    expect(screen.getAllByText('+1 LAP')).toHaveLength(2)
  })

  it('displays tire compound and age', () => {
    const positions: Position[] = [
      { driver_number: 1, position: 1, date: '2024-03-10T14:30:00Z' }
    ]

    const drivers: Driver[] = [
      {
        driver_number: 1,
        broadcast_name: 'M VERSTAPPEN',
        full_name: 'Max Verstappen',
        name_acronym: 'VER',
        team_name: 'Red Bull Racing',
        team_colour: '3671C6',
        headshot_url: null
      }
    ]

    const stints: Stint[] = [
      {
        driver_number: 1,
        stint_number: 1,
        compound: 'SOFT',
        tyre_age_at_start: 0,
        lap_start: 1,
        lap_end: null
      }
    ]

    useLiveRaceStore.setState({ positions, drivers, stints })

    render(<RaceTower />)

    expect(screen.getByText('0 laps')).toBeInTheDocument()
    // Check for tire indicator with SOFT compound (red)
    const tireIndicator = screen.getByTitle('SOFT')
    expect(tireIndicator).toHaveClass('bg-red-500')
  })

  it('displays correct tire colors for each compound', () => {
    const positions: Position[] = [
      { driver_number: 1, position: 1, date: '2024-03-10T14:30:00Z' },
      { driver_number: 2, position: 2, date: '2024-03-10T14:30:00Z' },
      { driver_number: 3, position: 3, date: '2024-03-10T14:30:00Z' }
    ]

    const drivers: Driver[] = [
      {
        driver_number: 1,
        broadcast_name: 'Driver 1',
        full_name: 'Driver One',
        name_acronym: 'DR1',
        team_name: 'Team 1',
        team_colour: '000000',
        headshot_url: null
      },
      {
        driver_number: 2,
        broadcast_name: 'Driver 2',
        full_name: 'Driver Two',
        name_acronym: 'DR2',
        team_name: 'Team 2',
        team_colour: '000000',
        headshot_url: null
      },
      {
        driver_number: 3,
        broadcast_name: 'Driver 3',
        full_name: 'Driver Three',
        name_acronym: 'DR3',
        team_name: 'Team 3',
        team_colour: '000000',
        headshot_url: null
      }
    ]

    const stints: Stint[] = [
      {
        driver_number: 1,
        stint_number: 1,
        compound: 'SOFT',
        tyre_age_at_start: 0,
        lap_start: 1,
        lap_end: null
      },
      {
        driver_number: 2,
        stint_number: 1,
        compound: 'MEDIUM',
        tyre_age_at_start: 0,
        lap_start: 1,
        lap_end: null
      },
      {
        driver_number: 3,
        stint_number: 1,
        compound: 'HARD',
        tyre_age_at_start: 0,
        lap_start: 1,
        lap_end: null
      }
    ]

    useLiveRaceStore.setState({ positions, drivers, stints })

    render(<RaceTower />)

    expect(screen.getByTitle('SOFT')).toHaveClass('bg-red-500')
    expect(screen.getByTitle('MEDIUM')).toHaveClass('bg-yellow-400')
    expect(screen.getByTitle('HARD')).toHaveClass('bg-gray-400')
  })

  it('displays interval to car ahead', () => {
    const positions: Position[] = [
      { driver_number: 1, position: 1, date: '2024-03-10T14:30:00Z' },
      { driver_number: 44, position: 2, date: '2024-03-10T14:30:00Z' }
    ]

    const intervals: Interval[] = [
      { driver_number: 1, gap_to_leader: null, interval: null, date: '2024-03-10T14:30:00Z' },
      { driver_number: 44, gap_to_leader: 3.456, interval: 3.456, date: '2024-03-10T14:30:00Z' }
    ]

    const drivers: Driver[] = [
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
        driver_number: 44,
        broadcast_name: 'L HAMILTON',
        full_name: 'Lewis Hamilton',
        name_acronym: 'HAM',
        team_name: 'Mercedes',
        team_colour: '27F4D2',
        headshot_url: null
      }
    ]

    useLiveRaceStore.setState({ positions, intervals, drivers })

    render(<RaceTower />)

    // P1 should show "—" for interval
    const rows = screen.getAllByRole('generic').filter(el => el.className.includes('flex items-center gap-4'))
    expect(rows[0]).toHaveTextContent('—')
  })

  it('uses React.memo for performance optimization', () => {
    // React.memo wraps the component, so we check it's a memo component
    expect(RaceTower.$$typeof.toString()).toContain('react.memo')
  })

  it('displays team color background for driver names', () => {
    const positions: Position[] = [
      { driver_number: 1, position: 1, date: '2024-03-10T14:30:00Z' }
    ]

    const drivers: Driver[] = [
      {
        driver_number: 1,
        broadcast_name: 'M VERSTAPPEN',
        full_name: 'Max Verstappen',
        name_acronym: 'VER',
        team_name: 'Red Bull Racing',
        team_colour: '3671C6',
        headshot_url: null
      }
    ]

    useLiveRaceStore.setState({ positions, drivers })

    const { container } = render(<RaceTower />)

    // Check for team color background (rendered as inline style with rgba)
    const driverInfo = container.querySelector('[style*="54, 113, 198"]')
    expect(driverInfo).toBeInTheDocument()
  })
})

/**
 * Property-Based Tests for RaceTower Component
 */

describe('Property 11: Position Ordering Invariant', () => {
  /**
   * Validates: Requirements 6.1
   * 
   * Test that Race Tower displays drivers in ascending order by position number.
   * For any random array of positions, the rendered order SHALL match sorted position values.
   */

  beforeEach(() => {
    useLiveRaceStore.setState({
      positions: [],
      intervals: [],
      drivers: [],
      stints: [],
      sessionInfo: null,
      pitStops: [],
      weather: null,
      raceControl: [],
      isConnected: false,
      lastUpdate: null,
      intervalHistory: []
    })
  })

  // Generator for random position arrays
  const positionArrayArb = fc.array(
    fc.record({
      driver_number: fc.integer({ min: 1, max: 99 }),
      position: fc.integer({ min: 1, max: 20 }),
      date: fc.constant('2024-03-10T14:30:00Z')
    }),
    { minLength: 1, maxLength: 20 }
  ).map(positions => {
    // Ensure unique positions (no two drivers can have same position)
    const uniquePositions = new Map<number, Position>()
    positions.forEach(pos => {
      if (!uniquePositions.has(pos.position)) {
        uniquePositions.set(pos.position, pos)
      }
    })
    return Array.from(uniquePositions.values())
  })

  // Generator for matching drivers
  const driversForPositionsArb = (positions: Position[]) => {
    return fc.constant(
      positions.map(pos => ({
        driver_number: pos.driver_number,
        broadcast_name: `Driver ${pos.driver_number}`,
        full_name: `Full Name ${pos.driver_number}`,
        name_acronym: `D${pos.driver_number}`,
        team_name: `Team ${pos.driver_number}`,
        team_colour: '000000',
        headshot_url: null
      }))
    )
  }

  it('Property: Drivers are always displayed in ascending position order', () => {
    fc.assert(
      fc.property(
        positionArrayArb.chain(positions => 
          fc.tuple(
            fc.constant(positions),
            driversForPositionsArb(positions)
          )
        ),
        ([positions, drivers]) => {
          // Set store state with random positions
          act(() => {
            useLiveRaceStore.setState({ positions, drivers })
          })

          const { container, unmount } = render(<RaceTower />)

          try {
            // Get all position numbers from rendered component
            const positionElements = container.querySelectorAll('.w-8.text-center.font-bold.text-lg')
            const renderedPositions = Array.from(positionElements).map(el => 
              parseInt(el.textContent || '0', 10)
            )

            // Verify positions are in ascending order
            const sortedPositions = [...renderedPositions].sort((a, b) => a - b)
            expect(renderedPositions).toEqual(sortedPositions)

            // Verify all positions from data are rendered
            const expectedPositions = positions.map(p => p.position).sort((a, b) => a - b)
            expect(renderedPositions).toEqual(expectedPositions)
          } finally {
            unmount()
          }
        }
      ),
      { numRuns: 50 }
    )
  })

  it('Property: Position ordering is stable across re-renders', () => {
    fc.assert(
      fc.property(
        positionArrayArb.chain(positions => 
          fc.tuple(
            fc.constant(positions),
            driversForPositionsArb(positions)
          )
        ),
        ([positions, drivers]) => {
          // Shuffle positions to simulate out-of-order data
          const shuffledPositions = [...positions].sort(() => Math.random() - 0.5)
          
          act(() => {
            useLiveRaceStore.setState({ positions: shuffledPositions, drivers })
          })

          const { container, rerender, unmount } = render(<RaceTower />)

          try {
            // Get first render order
            const getRenderedPositions = () => {
              const positionElements = container.querySelectorAll('.w-8.text-center.font-bold.text-lg')
              return Array.from(positionElements).map(el => parseInt(el.textContent || '0', 10))
            }

            const firstRender = getRenderedPositions()

            // Re-render with same data
            rerender(<RaceTower />)
            const secondRender = getRenderedPositions()

            // Verify order is stable
            expect(firstRender).toEqual(secondRender)

            // Verify order is correct (ascending)
            const sortedPositions = [...firstRender].sort((a, b) => a - b)
            expect(firstRender).toEqual(sortedPositions)
          } finally {
            unmount()
          }
        }
      ),
      { numRuns: 30 }
    )
  })
})

describe('Property 10: Complete Driver Information Display', () => {
  /**
   * Validates: Requirements 6.2-6.6
   * 
   * Test that all required fields are present for each driver:
   * - Driver number, name, team (Req 6.2)
   * - Gap to leader (Req 6.3)
   * - Interval to car ahead (Req 6.4)
   * - Tire compound (Req 6.5)
   * - Tire age (Req 6.6)
   */

  beforeEach(() => {
    useLiveRaceStore.setState({
      positions: [],
      intervals: [],
      drivers: [],
      stints: [],
      sessionInfo: null,
      pitStops: [],
      weather: null,
      raceControl: [],
      isConnected: false,
      lastUpdate: null,
      intervalHistory: []
    })
  })

  // Generator for complete race data
  const completeRaceDataArb = fc.record({
    numDrivers: fc.integer({ min: 1, max: 20 })
  }).chain(({ numDrivers }) => {
    const driverNumbers = fc.array(
      fc.integer({ min: 1, max: 99 }),
      { minLength: numDrivers, maxLength: numDrivers }
    ).map(nums => Array.from(new Set(nums)).slice(0, numDrivers))

    return driverNumbers.chain(driverNums => {
      const positions: Position[] = driverNums.map((num, idx) => ({
        driver_number: num,
        position: idx + 1,
        date: '2024-03-10T14:30:00Z'
      }))

      const intervals: Interval[] = driverNums.map((num, idx) => ({
        driver_number: num,
        gap_to_leader: idx === 0 ? null : Math.random() * 30,
        interval: idx === 0 ? null : Math.random() * 5,
        date: '2024-03-10T14:30:00Z'
      }))

      const drivers: Driver[] = driverNums.map(num => ({
        driver_number: num,
        broadcast_name: `Driver ${num}`,
        full_name: `Full Name ${num}`,
        name_acronym: `D${num}`,
        team_name: `Team ${num}`,
        team_colour: Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0'),
        headshot_url: null
      }))

      const compounds: Array<'SOFT' | 'MEDIUM' | 'HARD' | 'INTERMEDIATE' | 'WET'> = 
        ['SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET']

      const stints: Stint[] = driverNums.map(num => ({
        driver_number: num,
        stint_number: 1,
        compound: compounds[Math.floor(Math.random() * compounds.length)],
        tyre_age_at_start: Math.floor(Math.random() * 30),
        lap_start: 1,
        lap_end: null
      }))

      return fc.constant({ positions, intervals, drivers, stints })
    })
  })

  it('Property: All required driver information fields are rendered', () => {
    fc.assert(
      fc.property(completeRaceDataArb, ({ positions, intervals, drivers, stints }) => {
        act(() => {
          useLiveRaceStore.setState({ positions, intervals, drivers, stints })
        })

        const { container, unmount } = render(<RaceTower />)

        try {
          // For each driver, verify all required fields are present
          positions.forEach((pos, idx) => {
            const driver = drivers.find(d => d.driver_number === pos.driver_number)
            const interval = intervals.find(i => i.driver_number === pos.driver_number)
            const stint = stints.find(s => s.driver_number === pos.driver_number)

            // Requirement 6.2: Driver number, name, team
            expect(container).toHaveTextContent(driver!.broadcast_name)
            expect(container).toHaveTextContent(driver!.team_name)

            // Requirement 6.3: Gap to leader (P1 shows '—', others show gap)
            if (pos.position === 1) {
              // P1 should have at least one '—' for gap
              expect(container).toHaveTextContent('—')
            } else if (interval?.gap_to_leader !== null && interval?.gap_to_leader !== undefined) {
              // Other positions should show gap (either as number or string like "+1 LAP")
              const gapText = typeof interval.gap_to_leader === 'string' 
                ? interval.gap_to_leader 
                : `+${interval.gap_to_leader.toFixed(3)}s`
              expect(container).toHaveTextContent(gapText)
            }

            // Requirement 6.5: Tire compound
            if (stint) {
              const tireIndicator = container.querySelector(`[title="${stint.compound}"]`)
              expect(tireIndicator).toBeInTheDocument()
            }

            // Requirement 6.6: Tire age in laps
            if (stint) {
              expect(container).toHaveTextContent(`${stint.tyre_age_at_start} laps`)
            }
          })
        } finally {
          unmount()
        }
      }),
      { numRuns: 20 }
    )
  })

  it('Property: Driver information is complete regardless of data order', () => {
    fc.assert(
      fc.property(completeRaceDataArb, ({ positions, intervals, drivers, stints }) => {
        // Shuffle all arrays to simulate out-of-order data
        const shuffledPositions = [...positions].sort(() => Math.random() - 0.5)
        const shuffledIntervals = [...intervals].sort(() => Math.random() - 0.5)
        const shuffledDrivers = [...drivers].sort(() => Math.random() - 0.5)
        const shuffledStints = [...stints].sort(() => Math.random() - 0.5)

        act(() => {
          useLiveRaceStore.setState({
            positions: shuffledPositions,
            intervals: shuffledIntervals,
            drivers: shuffledDrivers,
            stints: shuffledStints
          })
        })

        const { container, unmount } = render(<RaceTower />)

        try {
          // Verify all drivers are rendered with complete information
          drivers.forEach(driver => {
            expect(container).toHaveTextContent(driver.broadcast_name)
            expect(container).toHaveTextContent(driver.team_name)
          })

          // Verify all tire compounds are rendered
          stints.forEach(stint => {
            const tireIndicator = container.querySelector(`[title="${stint.compound}"]`)
            expect(tireIndicator).toBeInTheDocument()
          })
        } finally {
          unmount()
        }
      }),
      { numRuns: 20 }
    )
  })

  it('Property: P1 always shows "—" for gap and interval', () => {
    fc.assert(
      fc.property(completeRaceDataArb, ({ positions, intervals, drivers, stints }) => {
        act(() => {
          useLiveRaceStore.setState({ positions, intervals, drivers, stints })
        })

        const { container, unmount } = render(<RaceTower />)

        try {
          // Find P1 row (first row in the sorted list)
          const rows = container.querySelectorAll('.flex.items-center.gap-4')
          const p1Row = rows[0]

          // P1 should have "—" for both gap and interval
          const dashes = p1Row.querySelectorAll(':scope > *')
          const dashTexts = Array.from(dashes).map(el => el.textContent)
          
          // Should have at least 2 "—" symbols (gap and interval)
          const dashCount = dashTexts.filter(text => text?.includes('—')).length
          expect(dashCount).toBeGreaterThanOrEqual(2)
        } finally {
          unmount()
        }
      }),
      { numRuns: 20 }
    )
  })

  it('Property: Lapped cars preserve "+1 LAP" format', () => {
    fc.assert(
      fc.property(
        fc.record({
          numDrivers: fc.integer({ min: 2, max: 10 }),
          numLapped: fc.integer({ min: 1, max: 5 })
        }).chain(({ numDrivers, numLapped }) => {
          // Ensure numLapped doesn't exceed numDrivers - 1 (P1 can't be lapped)
          const actualNumLapped = Math.min(numLapped, numDrivers - 1)
          const driverNumbers = Array.from({ length: numDrivers }, (_, i) => i + 1)
          
          const positions: Position[] = driverNumbers.map((num, idx) => ({
            driver_number: num,
            position: idx + 1,
            date: '2024-03-10T14:30:00Z'
          }))

          const intervals: Interval[] = driverNumbers.map((num, idx) => {
            // Only drivers NOT in P1 can be lapped
            const isLapped = idx > 0 && idx >= numDrivers - actualNumLapped
            return {
              driver_number: num,
              gap_to_leader: idx === 0 ? null : (isLapped ? '+1 LAP' : Math.random() * 30),
              interval: idx === 0 ? null : (isLapped ? '+1 LAP' : Math.random() * 5),
              date: '2024-03-10T14:30:00Z'
            }
          })

          const drivers: Driver[] = driverNumbers.map(num => ({
            driver_number: num,
            broadcast_name: `Driver ${num}`,
            full_name: `Full Name ${num}`,
            name_acronym: `D${num}`,
            team_name: `Team ${num}`,
            team_colour: '000000',
            headshot_url: null
          }))

          const stints: Stint[] = driverNumbers.map(num => ({
            driver_number: num,
            stint_number: 1,
            compound: 'MEDIUM' as const,
            tyre_age_at_start: 0,
            lap_start: 1,
            lap_end: null
          }))

          return fc.constant({ positions, intervals, drivers, stints, numLapped: actualNumLapped })
        }),
        ({ positions, intervals, drivers, stints, numLapped }) => {
          act(() => {
            useLiveRaceStore.setState({ positions, intervals, drivers, stints })
          })

          const { container, unmount } = render(<RaceTower />)

          try {
            // Verify "+1 LAP" appears for lapped cars
            const bodyText = container.textContent || ''
            const lappedCount = (bodyText.match(/\+1 LAP/g) || []).length
            // Each lapped car shows "+1 LAP" twice (gap and interval)
            expect(lappedCount).toBe(numLapped * 2)
          } finally {
            unmount()
          }
        }
      ),
      { numRuns: 20 }
    )
  })
})
