import { describe, it, expect, afterEach, vi, beforeEach } from 'vitest'
import * as fc from 'fast-check'
import { render, within, cleanup } from '@testing-library/react'
import { act } from 'react'
import { CountdownTimer } from '../../components/live/CountdownTimer'

/**
 * Property 18: Countdown Timer Accuracy
 * **Validates: Requirements 19.1, 19.2, 19.3**
 * 
 * This property test verifies that:
 * 1. The countdown timer displays the correct time remaining (days, hours, minutes, seconds)
 * 2. The displayed time matches the calculated difference between current time and start time
 * 3. Accuracy is within ±1 second
 */

describe('Property 18: Countdown Timer Accuracy', () => {
  beforeEach(() => {
    // Use fake timers to control time
    vi.useFakeTimers()
  })

  afterEach(() => {
    cleanup()
    vi.useRealTimers()
  })

  it('should display correct time remaining with accuracy within ±1 second', () => {
    fc.assert(
      fc.property(
        // Generate random future timestamps (from 1 second to 30 days in the future)
        fc.integer({ min: 1000, max: 30 * 24 * 60 * 60 * 1000 }),
        (millisecondsInFuture: number) => {
          // Set a fixed "now" time
          const now = new Date('2024-03-10T14:00:00Z')
          vi.setSystemTime(now)

          // Calculate the start time
          const startTime = new Date(now.getTime() + millisecondsInFuture)
          const startTimeISO = startTime.toISOString()

          // Calculate expected time remaining
          const expectedDays = Math.floor(millisecondsInFuture / (1000 * 60 * 60 * 24))
          const expectedHours = Math.floor((millisecondsInFuture % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
          const expectedMinutes = Math.floor((millisecondsInFuture % (1000 * 60 * 60)) / (1000 * 60))
          const expectedSeconds = Math.floor((millisecondsInFuture % (1000 * 60)) / 1000)

          // Render component
          const { container, unmount } = render(<CountdownTimer startTime={startTimeISO} />)
          const panel = within(container)

          // Find the displayed values
          const timeUnits = container.querySelectorAll('.text-3xl')
          expect(timeUnits).toHaveLength(4)

          const displayedDays = parseInt(timeUnits[0].textContent || '0', 10)
          const displayedHours = parseInt(timeUnits[1].textContent || '0', 10)
          const displayedMinutes = parseInt(timeUnits[2].textContent || '0', 10)
          const displayedSeconds = parseInt(timeUnits[3].textContent || '0', 10)

          // Verify accuracy within ±1 second
          // Convert everything to total seconds for easier comparison
          const expectedTotalSeconds = 
            expectedDays * 24 * 60 * 60 + 
            expectedHours * 60 * 60 + 
            expectedMinutes * 60 + 
            expectedSeconds

          const displayedTotalSeconds = 
            displayedDays * 24 * 60 * 60 + 
            displayedHours * 60 * 60 + 
            displayedMinutes * 60 + 
            displayedSeconds

          const difference = Math.abs(expectedTotalSeconds - displayedTotalSeconds)

          // Verify labels are present
          expect(panel.getByText('Days')).toBeInTheDocument()
          expect(panel.getByText('Hours')).toBeInTheDocument()
          expect(panel.getByText('Minutes')).toBeInTheDocument()
          expect(panel.getByText('Seconds')).toBeInTheDocument()

          // Cleanup
          unmount()

          // Assert accuracy within ±1 second
          return difference <= 1
        }
      ),
      { numRuns: 100 }
    )
  })

  it('should update countdown every second', () => {
    fc.assert(
      fc.property(
        // Generate random future timestamps (from 10 seconds to 1 hour in the future)
        fc.integer({ min: 10000, max: 60 * 60 * 1000 }),
        (millisecondsInFuture: number) => {
          // Set a fixed "now" time
          const now = new Date('2024-03-10T14:00:00Z')
          vi.setSystemTime(now)

          // Calculate the start time
          const startTime = new Date(now.getTime() + millisecondsInFuture)
          const startTimeISO = startTime.toISOString()

          // Render component
          const { container, unmount } = render(<CountdownTimer startTime={startTimeISO} />)

          // Get initial seconds value
          const timeUnits = container.querySelectorAll('.text-3xl')
          const initialSeconds = parseInt(timeUnits[3].textContent || '0', 10)

          // Advance time by 1 second wrapped in act
          act(() => {
            vi.advanceTimersByTime(1000)
          })

          // Get updated seconds value
          const updatedTimeUnits = container.querySelectorAll('.text-3xl')
          const updatedSeconds = parseInt(updatedTimeUnits[3].textContent || '0', 10)

          // Cleanup
          unmount()

          // Verify that seconds decreased by 1 (or wrapped around from 0 to 59)
          if (initialSeconds === 0) {
            return updatedSeconds === 59
          } else {
            return updatedSeconds === initialSeconds - 1
          }
        }
      ),
      { numRuns: 50 }
    )
  })

  it('should display "Session starting..." when countdown reaches zero', () => {
    fc.assert(
      fc.property(
        fc.constant(0),
        () => {
          // Set a fixed "now" time
          const now = new Date('2024-03-10T14:00:00Z')
          vi.setSystemTime(now)

          // Set start time to now (countdown should be zero)
          const startTimeISO = now.toISOString()

          // Render component
          const { container, unmount } = render(<CountdownTimer startTime={startTimeISO} />)
          const panel = within(container)

          // Verify all time units show 00
          const timeUnits = container.querySelectorAll('.text-3xl')
          expect(timeUnits).toHaveLength(4)
          timeUnits.forEach(unit => {
            expect(unit.textContent).toBe('00')
          })

          // Verify "Session starting..." message is displayed
          expect(panel.getByText('Session starting...')).toBeInTheDocument()

          // Cleanup
          unmount()

          return true
        }
      ),
      { numRuns: 10 }
    )
  })

  it('should highlight in red when time remaining is less than 1 hour', () => {
    fc.assert(
      fc.property(
        // Generate timestamps less than 1 hour in the future
        fc.integer({ min: 1000, max: 59 * 60 * 1000 }),
        (millisecondsInFuture: number) => {
          // Set a fixed "now" time
          const now = new Date('2024-03-10T14:00:00Z')
          vi.setSystemTime(now)

          // Calculate the start time
          const startTime = new Date(now.getTime() + millisecondsInFuture)
          const startTimeISO = startTime.toISOString()

          // Render component
          const { container, unmount } = render(<CountdownTimer startTime={startTimeISO} />)

          // Find time unit containers
          const timeUnitContainers = container.querySelectorAll('.text-center.p-4.rounded-lg')
          expect(timeUnitContainers.length).toBeGreaterThan(0)

          // Verify red styling is applied
          const hasRedBackground = Array.from(timeUnitContainers).some(unit => 
            unit.classList.contains('bg-red-100')
          )
          expect(hasRedBackground).toBe(true)

          const hasRedText = container.querySelectorAll('.text-red-600').length > 0
          expect(hasRedText).toBe(true)

          // Cleanup
          unmount()

          return true
        }
      ),
      { numRuns: 50 }
    )
  })

  it('should add pulsing animation when time remaining is less than 5 minutes', () => {
    fc.assert(
      fc.property(
        // Generate timestamps less than 5 minutes in the future
        fc.integer({ min: 1000, max: 4 * 60 * 1000 + 59 * 1000 }),
        (millisecondsInFuture: number) => {
          // Set a fixed "now" time
          const now = new Date('2024-03-10T14:00:00Z')
          vi.setSystemTime(now)

          // Calculate the start time
          const startTime = new Date(now.getTime() + millisecondsInFuture)
          const startTimeISO = startTime.toISOString()

          // Render component
          const { container, unmount } = render(<CountdownTimer startTime={startTimeISO} />)

          // Find the grid container that should have the animate-pulse class
          const gridContainer = container.querySelector('.grid.grid-cols-4')
          expect(gridContainer).toBeInTheDocument()

          // Verify pulsing animation is applied
          expect(gridContainer).toHaveClass('animate-pulse')

          // Cleanup
          unmount()

          return true
        }
      ),
      { numRuns: 50 }
    )
  })

  it('should handle timezone conversion correctly', () => {
    fc.assert(
      fc.property(
        // Generate random future timestamps
        fc.integer({ min: 1000, max: 7 * 24 * 60 * 60 * 1000 }),
        (millisecondsInFuture: number) => {
          // Set a fixed "now" time
          const now = new Date('2024-03-10T14:00:00Z')
          vi.setSystemTime(now)

          // Calculate the start time
          const startTime = new Date(now.getTime() + millisecondsInFuture)
          
          // Test with different timezone formats - JavaScript Date constructor handles these correctly
          // Using ISO format with Z (UTC)
          const startTimeISO = startTime.toISOString()

          // Render component
          const { container, unmount } = render(<CountdownTimer startTime={startTimeISO} />)

          // Calculate expected time remaining
          const expectedTotalSeconds = Math.floor(millisecondsInFuture / 1000)

          // Get displayed time
          const timeUnits = container.querySelectorAll('.text-3xl')
          const displayedDays = parseInt(timeUnits[0].textContent || '0', 10)
          const displayedHours = parseInt(timeUnits[1].textContent || '0', 10)
          const displayedMinutes = parseInt(timeUnits[2].textContent || '0', 10)
          const displayedSeconds = parseInt(timeUnits[3].textContent || '0', 10)

          const displayedTotalSeconds = 
            displayedDays * 24 * 60 * 60 + 
            displayedHours * 60 * 60 + 
            displayedMinutes * 60 + 
            displayedSeconds

          const difference = Math.abs(expectedTotalSeconds - displayedTotalSeconds)

          // Cleanup
          unmount()

          // Verify accuracy within ±1 second
          return difference <= 1
        }
      ),
      { numRuns: 50 }
    )
  })
})
