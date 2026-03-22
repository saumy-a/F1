---
title: Testing Standards
inclusion: auto
---

# Testing Standards for F1 Dashboard Migration

## Backend Testing (pytest + Hypothesis)

### Test Structure
```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_redis(monkeypatch):
    """Mock Redis client for testing"""
    class MockRedis:
        def __init__(self):
            self.store = {}
        async def get(self, key):
            return self.store.get(key)
        async def setex(self, key, ttl, value):
            self.store[key] = value
    
    mock = MockRedis()
    monkeypatch.setattr("app.cache.redis.redis_client", mock)
    return mock
```

### Property-Based Testing
```python
# tests/test_analytics_properties.py
from hypothesis import given, strategies as st
import hypothesis.strategies as st

@given(st.lists(st.integers(min_value=1, max_value=20), min_size=1, max_size=20))
def test_consistency_score_bounds(positions):
    """Consistency score must be between 0 and 100"""
    score = consistency_score(positions)
    assert 0 <= score <= 100

@given(st.lists(st.integers(min_value=1, max_value=20), min_size=2))
def test_consistency_score_idempotence(positions):
    """Applying consistency_score twice should give same result"""
    assert consistency_score(positions) == consistency_score(positions)
```

### Integration Testing
```python
# tests/test_routes.py
@pytest.mark.asyncio
async def test_driver_standings_endpoint(client, mock_redis):
    response = await client.get("/api/standings/drivers/2024")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all("position" in item for item in data)
```

## Frontend Testing (Vitest + React Testing Library)

### Component Testing
```typescript
// src/components/__tests__/DriverCard.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { DriverCard } from '../DriverCard'

describe('DriverCard', () => {
  it('renders driver information correctly', () => {
    render(<DriverCard driver={{ name: 'Max Verstappen', number: 1 }} />)
    expect(screen.getByText('Max Verstappen')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()
  })
})
```

### Hook Testing
```typescript
// src/hooks/__tests__/useStandings.test.ts
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { describe, it, expect } from 'vitest'
import { useDriverStandings } from '../useStandings'

const createWrapper = () => {
  const queryClient = new QueryClient()
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useDriverStandings', () => {
  it('fetches driver standings', async () => {
    const { result } = renderHook(() => useDriverStandings('2024'), {
      wrapper: createWrapper(),
    })
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toBeDefined()
  })
})
```

### MSW (Mock Service Worker) Setup
```typescript
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/standings/drivers/:year', ({ params }) => {
    return HttpResponse.json([
      {
        position: '1',
        points: '575',
        wins: '19',
        Driver: {
          driverId: 'verstappen',
          givenName: 'Max',
          familyName: 'Verstappen',
        },
        Constructors: [{ constructorId: 'red_bull', name: 'Red Bull' }],
      },
    ])
  }),
  
  http.get('/api/analytics/trends/:driverId/:year', ({ params }) => {
    return HttpResponse.json({
      data: [[1, 2, 1, 3, 1]],
      layout: { title: 'Performance Trends' },
    })
  }),
]

// src/mocks/server.ts
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

export const server = setupServer(...handlers)

// src/setupTests.ts
import { beforeAll, afterEach, afterAll } from 'vitest'
import { server } from './mocks/server'

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### Vitest Configuration
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'src/setupTests.ts'],
    },
  },
})
```

## Coverage Requirements

- Backend: Minimum 80% code coverage
- Frontend: Minimum 70% code coverage
- All service layer functions must have unit tests
- All API endpoints must have integration tests
- All analytics functions must have property-based tests
- All React components must have component tests
- All custom hooks must have hook tests

## Running Tests

```bash
# Backend tests
cd backend && pytest tests/ --cov=app --cov-report=html -v

# Backend property tests only
pytest tests/test_analytics_properties.py -v

# Frontend tests
cd frontend && npx vitest run

# Frontend with coverage
npx vitest run --coverage

# Watch mode (development)
npx vitest
```
