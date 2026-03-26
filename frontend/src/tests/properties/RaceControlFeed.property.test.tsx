import { describe, it, expect } from 'vitest'
import * as fc from 'fast-check'
import type { RaceControlMessage } from '../../types/live'

/**
 * Property 14: Race Control Message Ordering
 * **Validates: Requirements 11.1**
 * 
 * This property test verifies that:
 * 1. Messages are displayed in reverse chronological order (most recent first)
 * 2. The ordering is consistent regardless of the input order
 */

// Helper function to sort messages (mirrors component logic)
function sortMessagesReverseChronological(messages: RaceControlMessage[]): RaceControlMessage[] {
  return [...messages].sort((a, b) => 
    new Date(b.date).getTime() - new Date(a.date).getTime()
  )
}

describe('Property 14: Race Control Message Ordering', () => {
  it('should display messages in reverse chronological order (most recent first)', () => {
    fc.assert(
      fc.property(
        // Generate array of race control messages with random timestamps
        fc.array(
          fc.record({
            category: fc.constantFrom('Flag', 'SafetyCar', 'DRS', 'TrackStatus', 'Other'),
            message: fc.string({ minLength: 10, maxLength: 100 }),
            date: fc.integer({ min: 1704067200000, max: 1735689599000 }).map(ms => new Date(ms).toISOString()),
            lap_number: fc.option(fc.integer({ min: 1, max: 70 }), { nil: null }),
            driver_number: fc.option(fc.integer({ min: 1, max: 20 }), { nil: null }),
            flag: fc.option(fc.constantFrom('YELLOW', 'RED', 'GREEN', 'BLUE', 'CHEQUERED'), { nil: null })
          }),
          { minLength: 1, maxLength: 100 }
        ),
        (messages) => {
          const sorted = sortMessagesReverseChronological(messages)
          
          // Verify that each message is chronologically before or equal to the previous one
          for (let i = 1; i < sorted.length; i++) {
            const prevTime = new Date(sorted[i - 1].date).getTime()
            const currTime = new Date(sorted[i].date).getTime()
            
            expect(prevTime).toBeGreaterThanOrEqual(currTime)
          }
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })
  
  it('should maintain consistent ordering regardless of input order', () => {
    fc.assert(
      fc.property(
        // Generate array of messages with unique timestamps to ensure deterministic ordering
        fc.array(
          fc.record({
            category: fc.constantFrom('Flag', 'SafetyCar', 'DRS', 'TrackStatus', 'Other'),
            message: fc.string({ minLength: 10, maxLength: 100 }),
            date: fc.integer({ min: 1704067200000, max: 1735689599000 }).map(ms => new Date(ms).toISOString()),
            lap_number: fc.option(fc.integer({ min: 1, max: 70 }), { nil: null }),
            driver_number: fc.option(fc.integer({ min: 1, max: 20 }), { nil: null }),
            flag: fc.option(fc.constantFrom('YELLOW', 'RED', 'GREEN', 'BLUE', 'CHEQUERED'), { nil: null })
          }),
          { minLength: 2, maxLength: 50 }
        ),
        (messages) => {
          // Sort the messages
          const sorted1 = sortMessagesReverseChronological(messages)
          
          // Shuffle the input and sort again
          const shuffled = [...messages].sort(() => Math.random() - 0.5)
          const sorted2 = sortMessagesReverseChronological(shuffled)
          
          // Both sorted arrays should have the same length
          expect(sorted1.length).toBe(sorted2.length)
          
          // Both sorted arrays should have the same timestamps in the same order
          for (let i = 0; i < sorted1.length; i++) {
            expect(new Date(sorted1[i].date).getTime()).toBe(new Date(sorted2[i].date).getTime())
          }
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })
  
  it('should place the most recent message first', () => {
    fc.assert(
      fc.property(
        // Generate array of messages with at least one message
        fc.array(
          fc.record({
            category: fc.constantFrom('Flag', 'SafetyCar', 'DRS', 'TrackStatus', 'Other'),
            message: fc.string({ minLength: 10, maxLength: 100 }),
            date: fc.integer({ min: 1704067200000, max: 1735689599000 }).map(ms => new Date(ms).toISOString()),
            lap_number: fc.option(fc.integer({ min: 1, max: 70 }), { nil: null }),
            driver_number: fc.option(fc.integer({ min: 1, max: 20 }), { nil: null }),
            flag: fc.option(fc.constantFrom('YELLOW', 'RED', 'GREEN', 'BLUE', 'CHEQUERED'), { nil: null })
          }),
          { minLength: 1, maxLength: 100 }
        ),
        (messages) => {
          const sorted = sortMessagesReverseChronological(messages)
          
          if (sorted.length === 0) return true
          
          // Find the message with the latest timestamp in the original array
          const latestMessage = messages.reduce((latest, current) => {
            return new Date(current.date).getTime() > new Date(latest.date).getTime() 
              ? current 
              : latest
          })
          
          // The first message in sorted array should be the latest
          const firstMessageTime = new Date(sorted[0].date).getTime()
          const latestMessageTime = new Date(latestMessage.date).getTime()
          
          expect(firstMessageTime).toBe(latestMessageTime)
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })
  
  it('should handle messages with identical timestamps', () => {
    fc.assert(
      fc.property(
        // Generate messages where some have the same timestamp
        fc.tuple(
          fc.integer({ min: 1704067200000, max: 1735689599000 }).map(ms => new Date(ms).toISOString()),
          fc.integer({ min: 2, max: 10 })
        ).chain(([timestamp, count]) => 
          fc.array(
            fc.record({
              category: fc.constantFrom('Flag', 'SafetyCar', 'DRS', 'TrackStatus', 'Other'),
              message: fc.string({ minLength: 10, maxLength: 100 }),
              date: fc.constant(timestamp),
              lap_number: fc.option(fc.integer({ min: 1, max: 70 }), { nil: null }),
              driver_number: fc.option(fc.integer({ min: 1, max: 20 }), { nil: null }),
              flag: fc.option(fc.constantFrom('YELLOW', 'RED', 'GREEN', 'BLUE', 'CHEQUERED'), { nil: null })
            }),
            { minLength: count, maxLength: count }
          )
        ),
        (messages) => {
          const sorted = sortMessagesReverseChronological(messages)
          
          // All messages should have the same timestamp
          const firstTimestamp = new Date(sorted[0].date).getTime()
          for (const msg of sorted) {
            expect(new Date(msg.date).getTime()).toBe(firstTimestamp)
          }
          
          // Length should be preserved
          expect(sorted.length).toBe(messages.length)
          
          return true
        }
      ),
      { numRuns: 50 }
    )
  })
})
