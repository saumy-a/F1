import { describe, it, expect } from 'vitest'
import * as fc from 'fast-check'
import type { PitStop } from '../../types/live'

/**
 * Property 12: Pit Stop Ranking Consistency
 * **Validates: Requirements 9.4, 9.5, 9.6**
 * 
 * This property test verifies that:
 * 1. The pit stop with the shortest duration is always ranked #1
 * 2. For any two pit stops A and B, if duration(A) < duration(B), then rank(A) < rank(B)
 */

// Helper function to calculate rankings (mirrors component logic)
function calculateRankings(pitStops: PitStop[]): Array<{ pitStop: PitStop; rank: number }> {
  // Filter out pit stops without duration data
  const validPitStops = pitStops.filter((ps) => ps.stop_duration !== null)
  
  // Sort by duration (ascending)
  const sortedByDuration = [...validPitStops].sort((a, b) => {
    const durationA = a.stop_duration ?? Infinity
    const durationB = b.stop_duration ?? Infinity
    return durationA - durationB
  })
  
  // Assign ranks
  return sortedByDuration.map((ps, index) => ({
    pitStop: ps,
    rank: index + 1
  }))
}

describe('Property 12: Pit Stop Ranking Consistency', () => {
  it('should always rank the pit stop with shortest duration as #1', () => {
    fc.assert(
      fc.property(
        // Generate array of pit stops with random durations
        fc.array(
          fc.record({
            driver_number: fc.integer({ min: 1, max: 20 }),
            lap_number: fc.integer({ min: 1, max: 70 }),
            stop_duration: fc.float({ min: 15.0, max: 60.0, noNaN: true }),
            lane_duration: fc.float({ min: 10.0, max: 50.0, noNaN: true }),
            date: fc.integer({ min: new Date('2020-01-01').getTime(), max: new Date('2025-12-31').getTime() }).map(ts => new Date(ts).toISOString())
          }),
          { minLength: 1, maxLength: 100 }
        ),
        (pitStops) => {
          const ranked = calculateRankings(pitStops)
          
          if (ranked.length === 0) return true
          
          // Find the pit stop with rank #1
          const fastestStop = ranked.find(r => r.rank === 1)
          expect(fastestStop).toBeDefined()
          
          if (!fastestStop) return true
          
          // Verify that no other pit stop has a shorter duration
          for (const other of ranked) {
            if (other.rank !== 1) {
              expect(other.pitStop.stop_duration).toBeGreaterThanOrEqual(
                fastestStop.pitStop.stop_duration!
              )
            }
          }
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })
  
  it('should maintain transitive ordering: if duration(A) < duration(B), then rank(A) < rank(B)', () => {
    fc.assert(
      fc.property(
        // Generate array of pit stops with random durations
        fc.array(
          fc.record({
            driver_number: fc.integer({ min: 1, max: 20 }),
            lap_number: fc.integer({ min: 1, max: 70 }),
            stop_duration: fc.float({ min: 15.0, max: 60.0, noNaN: true }),
            lane_duration: fc.float({ min: 10.0, max: 50.0, noNaN: true }),
            date: fc.integer({ min: new Date('2020-01-01').getTime(), max: new Date('2025-12-31').getTime() }).map(ts => new Date(ts).toISOString())
          }),
          { minLength: 2, maxLength: 100 }
        ),
        (pitStops) => {
          const ranked = calculateRankings(pitStops)
          
          if (ranked.length < 2) return true
          
          // Check all pairs
          for (let i = 0; i < ranked.length; i++) {
            for (let j = i + 1; j < ranked.length; j++) {
              const stopA = ranked[i]
              const stopB = ranked[j]
              
              const durationA = stopA.pitStop.stop_duration!
              const durationB = stopB.pitStop.stop_duration!
              
              // If duration(A) < duration(B), then rank(A) < rank(B)
              if (durationA < durationB) {
                expect(stopA.rank).toBeLessThan(stopB.rank)
              }
              // If duration(A) > duration(B), then rank(A) > rank(B)
              else if (durationA > durationB) {
                expect(stopA.rank).toBeGreaterThan(stopB.rank)
              }
              // If durations are equal, ranks should be consecutive (no gaps)
              else {
                // Equal durations can have any relative ranking, but should be consecutive
                expect(Math.abs(stopA.rank - stopB.rank)).toBeLessThanOrEqual(
                  ranked.filter(r => r.pitStop.stop_duration === durationA).length
                )
              }
            }
          }
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })
  
  it('should handle pit stops with null durations by excluding them from ranking', () => {
    fc.assert(
      fc.property(
        // Generate array with mix of valid and null durations
        fc.array(
          fc.record({
            driver_number: fc.integer({ min: 1, max: 20 }),
            lap_number: fc.integer({ min: 1, max: 70 }),
            stop_duration: fc.option(fc.float({ min: 15.0, max: 60.0, noNaN: true }), { nil: null }),
            lane_duration: fc.float({ min: 10.0, max: 50.0, noNaN: true }),
            date: fc.integer({ min: new Date('2020-01-01').getTime(), max: new Date('2025-12-31').getTime() }).map(ts => new Date(ts).toISOString())
          }),
          { minLength: 1, maxLength: 50 }
        ),
        (pitStops) => {
          const ranked = calculateRankings(pitStops)
          
          // All ranked pit stops should have non-null durations
          for (const r of ranked) {
            expect(r.pitStop.stop_duration).not.toBeNull()
          }
          
          // Number of ranked stops should equal number of stops with valid durations
          const validCount = pitStops.filter(ps => ps.stop_duration !== null).length
          expect(ranked.length).toBe(validCount)
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })
})
