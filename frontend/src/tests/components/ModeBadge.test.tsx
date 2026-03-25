import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ModeBadge } from '../../components/live/ModeBadge'
import type { SessionInfo } from '../../types/live'

const createMockSession = (overrides?: Partial<SessionInfo>): SessionInfo => ({
  session_key: '9158',
  session_name: 'Race',
  session_type: 'Race',
  date_start: '2023-05-28T13:00:00Z',
  date_end: '2023-05-28T15:00:00Z',
  gmt_offset: '+02:00',
  location: 'Monaco',
  country_name: 'Monaco',
  circuit_short_name: 'Monaco',
  mode: 'live',
  ...overrides,
})

describe('ModeBadge', () => {
  it('displays live badge with pulse animation', () => {
    const sessionInfo = createMockSession({ mode: 'live' })
    render(<ModeBadge mode="live" sessionInfo={sessionInfo} />)
    
    expect(screen.getByText('LIVE')).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'Session mode: LIVE')
    
    // Check for red background
    const badge = screen.getByRole('status')
    expect(badge).toHaveClass('bg-red-600')
    expect(badge).toHaveClass('text-white')
    
    // Check for pulse animation elements
    const pulseElements = badge.querySelectorAll('.animate-ping')
    expect(pulseElements.length).toBeGreaterThan(0)
  })

  it('displays upcoming badge without animation', () => {
    const sessionInfo = createMockSession({ mode: 'upcoming' })
    render(<ModeBadge mode="upcoming" sessionInfo={sessionInfo} />)
    
    expect(screen.getByText('UPCOMING')).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'Session mode: UPCOMING')
    
    // Check for amber background
    const badge = screen.getByRole('status')
    expect(badge).toHaveClass('bg-amber-500')
    expect(badge).toHaveClass('text-gray-900')
    
    // Check no pulse animation
    const pulseElements = badge.querySelectorAll('.animate-ping')
    expect(pulseElements.length).toBe(0)
  })

  it('displays replay badge with circuit and year', () => {
    const sessionInfo = createMockSession({
      mode: 'replay',
      circuit_short_name: 'Monaco',
      date_start: '2023-05-28T13:00:00Z'
    })
    render(<ModeBadge mode="replay" sessionInfo={sessionInfo} />)
    
    expect(screen.getByText(/REPLAY — Monaco 2023/)).toBeInTheDocument()
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'Session mode: REPLAY — Monaco 2023')
    
    // Check for blue background
    const badge = screen.getByRole('status')
    expect(badge).toHaveClass('bg-blue-600')
    expect(badge).toHaveClass('text-white')
    
    // Check no pulse animation
    const pulseElements = badge.querySelectorAll('.animate-ping')
    expect(pulseElements.length).toBe(0)
  })

  it('has sticky positioning and proper z-index', () => {
    const sessionInfo = createMockSession({ mode: 'live' })
    render(<ModeBadge mode="live" sessionInfo={sessionInfo} />)
    
    const badge = screen.getByRole('status')
    expect(badge).toHaveClass('sticky')
    expect(badge).toHaveClass('top-4')
    expect(badge).toHaveClass('z-50')
  })

  it('has rounded pill shape', () => {
    const sessionInfo = createMockSession({ mode: 'live' })
    render(<ModeBadge mode="live" sessionInfo={sessionInfo} />)
    
    const badge = screen.getByRole('status')
    expect(badge).toHaveClass('rounded-full')
  })

  it('extracts year correctly from date_start', () => {
    const sessionInfo = createMockSession({
      mode: 'replay',
      circuit_short_name: 'Silverstone',
      date_start: '2024-07-07T14:00:00Z'
    })
    render(<ModeBadge mode="replay" sessionInfo={sessionInfo} />)
    
    expect(screen.getByText(/REPLAY — Silverstone 2024/)).toBeInTheDocument()
  })
})
