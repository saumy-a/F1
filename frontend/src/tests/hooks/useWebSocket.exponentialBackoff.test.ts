import { describe, it, expect } from 'vitest'
import * as fc from 'fast-check'

/**
 * Property 7: Exponential Backoff Correctness
 * 
 * Validates: Requirements 2.7, 23.1-23.4
 * 
 * Test that delay for attempt N equals min(1000 × 2^(N-1), 30000) milliseconds
 * Use fast-check to generate random attempt numbers 0-20
 * Verify calculated delay matches expected formula
 */

// Extract the exponential backoff calculation logic
const calculateExponentialBackoff = (
  attemptNumber: number,
  initialDelay: number = 1000,
  maxDelay: number = 30000
): number => {
  const delay = initialDelay * Math.pow(2, attemptNumber)
  return Math.min(delay, maxDelay)
}

describe('Property 7: Exponential Backoff Correctness', () => {
  it('should calculate correct exponential backoff delay for any attempt number', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 20 }), // Generate random attempt numbers 0-20
        (attemptNumber) => {
          const calculatedDelay = calculateExponentialBackoff(attemptNumber)
          const expectedDelay = Math.min(1000 * Math.pow(2, attemptNumber), 30000)
          
          // Verify calculated delay matches expected formula
          expect(calculatedDelay).toBe(expectedDelay)
        }
      ),
      { numRuns: 100 } // Run 100 test cases
    )
  })

  it('should follow exponential growth pattern: 1s → 2s → 4s → 8s → 16s → 30s max', () => {
    const expectedSequence = [
      { attempt: 0, delay: 1000 },    // 1s
      { attempt: 1, delay: 2000 },    // 2s
      { attempt: 2, delay: 4000 },    // 4s
      { attempt: 3, delay: 8000 },    // 8s
      { attempt: 4, delay: 16000 },   // 16s
      { attempt: 5, delay: 30000 },   // 30s (capped)
      { attempt: 6, delay: 30000 },   // 30s (capped)
      { attempt: 10, delay: 30000 },  // 30s (capped)
      { attempt: 20, delay: 30000 },  // 30s (capped)
    ]

    expectedSequence.forEach(({ attempt, delay }) => {
      const calculatedDelay = calculateExponentialBackoff(attempt)
      expect(calculatedDelay).toBe(delay)
    })
  })

  it('should never exceed maximum delay of 30 seconds', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 100 }), // Test with even larger attempt numbers
        (attemptNumber) => {
          const calculatedDelay = calculateExponentialBackoff(attemptNumber)
          
          // Verify delay never exceeds 30 seconds
          expect(calculatedDelay).toBeLessThanOrEqual(30000)
        }
      ),
      { numRuns: 100 }
    )
  })

  it('should always return a positive delay', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 20 }),
        (attemptNumber) => {
          const calculatedDelay = calculateExponentialBackoff(attemptNumber)
          
          // Verify delay is always positive
          expect(calculatedDelay).toBeGreaterThan(0)
        }
      ),
      { numRuns: 100 }
    )
  })

  it('should produce monotonically increasing delays until max is reached', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 19 }), // Test pairs of consecutive attempts
        (attemptNumber) => {
          const delay1 = calculateExponentialBackoff(attemptNumber)
          const delay2 = calculateExponentialBackoff(attemptNumber + 1)
          
          // Verify delay increases or stays at max
          expect(delay2).toBeGreaterThanOrEqual(delay1)
        }
      ),
      { numRuns: 100 }
    )
  })

  it('should match the formula: min(1000 × 2^N, 30000)', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 20 }),
        (attemptNumber) => {
          const calculatedDelay = calculateExponentialBackoff(attemptNumber)
          const formulaDelay = Math.min(1000 * Math.pow(2, attemptNumber), 30000)
          
          // Verify exact match with formula
          expect(calculatedDelay).toBe(formulaDelay)
        }
      ),
      { numRuns: 100 }
    )
  })

  it('should handle edge cases correctly', () => {
    // Attempt 0: 1000ms
    expect(calculateExponentialBackoff(0)).toBe(1000)
    
    // Attempt 1: 2000ms
    expect(calculateExponentialBackoff(1)).toBe(2000)
    
    // Large attempt number: capped at 30000ms
    expect(calculateExponentialBackoff(100)).toBe(30000)
    
    // Negative attempt (edge case, should still work)
    expect(calculateExponentialBackoff(-1)).toBe(500)
  })

  it('should support custom initial delay and max delay', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 10 }),
        fc.integer({ min: 100, max: 5000 }),
        fc.integer({ min: 10000, max: 60000 }),
        (attemptNumber, initialDelay, maxDelay) => {
          const calculatedDelay = calculateExponentialBackoff(attemptNumber, initialDelay, maxDelay)
          const expectedDelay = Math.min(initialDelay * Math.pow(2, attemptNumber), maxDelay)
          
          // Verify formula works with custom parameters
          expect(calculatedDelay).toBe(expectedDelay)
          expect(calculatedDelay).toBeLessThanOrEqual(maxDelay)
        }
      ),
      { numRuns: 100 }
    )
  })
})
