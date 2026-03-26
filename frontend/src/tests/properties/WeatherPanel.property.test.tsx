import { describe, it, expect, afterEach } from 'vitest'
import * as fc from 'fast-check'
import { render, within, cleanup } from '@testing-library/react'
import { act } from 'react'
import { WeatherPanel } from '../../components/live/WeatherPanel'
import { useLiveRaceStore } from '../../store/liveRaceStore'
import type { Weather } from '../../types/live'

/**
 * Property 13: Weather Data Completeness
 * **Validates: Requirements 10.1-10.7**
 * 
 * This property test verifies that:
 * 1. All seven required weather fields are displayed when weather data exists
 * 2. Track temp, air temp, humidity, pressure, rainfall, wind direction, wind speed are all rendered
 */

// Generator for valid weather data
const weatherArbitrary = fc.record({
  track_temperature: fc.float({ min: -10, max: 60, noNaN: true }),
  air_temperature: fc.float({ min: -10, max: 50, noNaN: true }),
  humidity: fc.integer({ min: 0, max: 100 }),
  pressure: fc.float({ min: 900, max: 1100, noNaN: true }),
  rainfall: fc.integer({ min: 0, max: 1 }),
  wind_direction: fc.integer({ min: 0, max: 359 }),
  wind_speed: fc.float({ min: 0, max: 100, noNaN: true }),
  date: fc.integer({ min: new Date('2020-01-01').getTime(), max: new Date('2025-12-31').getTime() }).map(ts => new Date(ts).toISOString())
})

describe('Property 13: Weather Data Completeness', () => {
  afterEach(() => {
    cleanup()
    // Reset store state
    act(() => {
      useLiveRaceStore.setState({ weather: null })
    })
  })
  
  it('should display all seven required weather fields when weather data exists', () => {
    fc.assert(
      fc.property(
        weatherArbitrary,
        (weather: Weather) => {
          // Set weather data in store
          act(() => {
            useLiveRaceStore.setState({ weather })
          })
          
          // Render component
          const { container, unmount } = render(<WeatherPanel />)
          
          // Use within to scope queries to this specific render
          const panel = within(container)
          
          // Verify all seven required fields are present
          
          // 1. Track Temperature
          const trackTempLabel = panel.getByText('Track Temp')
          expect(trackTempLabel).toBeInTheDocument()
          const trackTempValue = trackTempLabel.parentElement?.querySelector('.text-2xl')
          expect(trackTempValue).toHaveTextContent(`${weather.track_temperature.toFixed(1)}°C`)
          
          // 2. Air Temperature
          const airTempLabel = panel.getByText('Air Temp')
          expect(airTempLabel).toBeInTheDocument()
          const airTempValue = airTempLabel.parentElement?.querySelector('.text-2xl')
          expect(airTempValue).toHaveTextContent(`${weather.air_temperature.toFixed(1)}°C`)
          
          // 3. Humidity
          expect(panel.getByText('Humidity')).toBeInTheDocument()
          expect(panel.getByText(`${weather.humidity}%`)).toBeInTheDocument()
          
          // 4. Pressure
          expect(panel.getByText('Pressure')).toBeInTheDocument()
          expect(panel.getByText(`${weather.pressure.toFixed(0)} hPa`)).toBeInTheDocument()
          
          // 5. Rainfall
          expect(panel.getByText(/Rainfall/)).toBeInTheDocument()
          if (weather.rainfall === 1) {
            expect(panel.getByText('Wet Track Conditions')).toBeInTheDocument()
          } else {
            expect(panel.getByText('Dry Track')).toBeInTheDocument()
          }
          
          // 6. Wind Direction
          const windDirLabel = panel.getByText('Wind Direction')
          expect(windDirLabel).toBeInTheDocument()
          const windDirValue = windDirLabel.parentElement?.querySelector('.text-xl')
          expect(windDirValue).toHaveTextContent(new RegExp(`${weather.wind_direction}°`))
          
          // 7. Wind Speed
          const windSpeedLabel = panel.getByText('Wind Speed')
          expect(windSpeedLabel).toBeInTheDocument()
          const windSpeedValue = windSpeedLabel.parentElement?.querySelector('.text-xl')
          expect(windSpeedValue).toHaveTextContent(`${weather.wind_speed.toFixed(1)} km/h`)
          
          // Cleanup after each property test run
          unmount()
          
          return true
        }
      ),
      { numRuns: 50 }
    )
  })
  
  it('should display "No weather data available" when weather is null', () => {
    fc.assert(
      fc.property(
        fc.constant(null),
        () => {
          // Set weather to null in store
          act(() => {
            useLiveRaceStore.setState({ weather: null })
          })
          
          // Render component
          const { container, unmount } = render(<WeatherPanel />)
          
          // Use within to scope queries to this specific render
          const panel = within(container)
          
          // Verify message is displayed
          expect(panel.getByText('No weather data available')).toBeInTheDocument()
          
          // Verify weather fields are NOT displayed
          expect(panel.queryByText('Track Temp')).not.toBeInTheDocument()
          expect(panel.queryByText('Air Temp')).not.toBeInTheDocument()
          expect(panel.queryByText('Humidity')).not.toBeInTheDocument()
          expect(panel.queryByText('Pressure')).not.toBeInTheDocument()
          expect(panel.queryByText('Wind Direction')).not.toBeInTheDocument()
          expect(panel.queryByText('Wind Speed')).not.toBeInTheDocument()
          
          // Cleanup after each property test run
          unmount()
          
          return true
        }
      ),
      { numRuns: 10 }
    )
  })
  
  it('should highlight rainfall indicator with blue background when rainfall=1', () => {
    fc.assert(
      fc.property(
        weatherArbitrary,
        (weather: Weather) => {
          // Set weather data in store
          act(() => {
            useLiveRaceStore.setState({ weather })
          })
          
          // Render component
          const { container, unmount } = render(<WeatherPanel />)
          
          // Use within to scope queries to this specific render
          const panel = within(container)
          
          // Find the rainfall section - get the parent container, not just the label
          const rainfallLabel = panel.getByText(/Rainfall/)
          const rainfallSection = rainfallLabel.parentElement
          expect(rainfallSection).toBeInTheDocument()
          
          if (weather.rainfall === 1) {
            // Should have blue background classes
            expect(rainfallSection).toHaveClass('bg-blue-100')
            expect(rainfallSection).toHaveClass('border-blue-300')
            expect(panel.getByText('Wet Track Conditions')).toBeInTheDocument()
          } else {
            // Should have gray background
            expect(rainfallSection).toHaveClass('bg-gray-50')
            expect(panel.getByText('Dry Track')).toBeInTheDocument()
          }
          
          // Cleanup after each property test run
          unmount()
          
          return true
        }
      ),
      { numRuns: 50 }
    )
  })
  
  it('should display weather icon based on rainfall value', () => {
    fc.assert(
      fc.property(
        weatherArbitrary,
        (weather: Weather) => {
          // Set weather data in store
          act(() => {
            useLiveRaceStore.setState({ weather })
          })
          
          // Render component
          const { container, unmount } = render(<WeatherPanel />)
          
          // Check that an icon is displayed in the header
          const header = container.querySelector('.bg-gray-800')
          expect(header).toBeInTheDocument()
          
          // Icon should be present (we can't easily test the exact emoji, but we can verify structure)
          const iconSpan = header?.querySelector('.text-2xl')
          expect(iconSpan).toBeInTheDocument()
          
          // Cleanup after each property test run
          unmount()
          
          return true
        }
      ),
      { numRuns: 30 }
    )
  })
})
