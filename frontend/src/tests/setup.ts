import { afterEach, beforeAll, afterAll } from 'vitest'
import { cleanup } from '@testing-library/react'
import '@testing-library/jest-dom'
import { server } from './mocks/server'

// Start MSW server before all tests
beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' })
})

// Reset handlers after each test
afterEach(() => {
  server.resetHandlers()
  cleanup()
})

// Close server after all tests
afterAll(() => {
  server.close()
})

// Mock environment variables
process.env.VITE_API_BASE_URL = 'http://localhost:8000'
process.env.VITE_WS_BASE_URL = 'ws://localhost:8000'

