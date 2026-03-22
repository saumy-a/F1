# Implementation Plan: F1 Dashboard Migration to FastAPI + React

## Overview

This implementation plan breaks down the migration of the Streamlit F1 Dashboard (~5200 lines) into a modern FastAPI backend + React frontend architecture. The plan follows a 12-phase approach that incrementally extracts functionality, builds the new architecture, and ensures feature parity with comprehensive testing.

The migration prioritizes:
- Incremental progress with working code at each checkpoint
- Early validation through automated tests
- Clear separation of concerns (data, business logic, presentation)
- Real-time capabilities via WebSocket
- Production-ready containerization

## Tasks

- [ ] 1. Project setup and service layer extraction
  - [ ] 1.1 Create backend project structure
    - Create `backend/` directory with subdirectories: `app/`, `app/routers/`, `app/services/`, `app/models/`, `app/cache/`, `app/middleware/`, `app/utils/`, `tests/`
    - Create `requirements.txt` with FastAPI, uvicorn, httpx, redis, pydantic, pytest, hypothesis
    - Create `.env.example` with environment variable templates
    - _Requirements: 1.1, 1.2_
  
  - [ ] 1.2 Extract Jolpica service functions from Streamlit app
    - Create `app/services/jolpica.py` with 7 async functions: `fetch_driver_standings`, `fetch_constructor_standings`, `fetch_race_schedule`, `fetch_race_results`, `fetch_qualifying_results`, `fetch_lap_times`, `fetch_driver_race_results`
    - Use httpx.AsyncClient with connection pooling
    - Add error handling and logging with request IDs
    - _Requirements: 1.1, 1.3, 2.1_
  
  - [ ]* 1.3 Write unit tests for Jolpica service
    - Test each service function with mocked httpx responses
    - Test error handling for API failures
    - _Requirements: 4.1_
  
  - [ ] 1.4 Extract analytics calculation functions
    - Create `app/services/analytics.py` with 15 calculation functions matching existing Streamlit logic
    - Ensure identical outputs to Streamlit for consistency score, DNF rate, performance trends, form indicator, etc.
    - Add helper functions in `app/utils/helpers.py`: `safe_int`, `safe_float`, `safe_divide`, `is_dnf`
    - _Requirements: 1.1, 2.2, 2.3_

- [ ] 2. FastAPI application scaffold and configuration
  - [ ] 2.1 Create FastAPI application with lifespan management
    - Create `app/main.py` with FastAPI app, lifespan context manager for Redis init/cleanup
    - Create `app/config.py` with Pydantic Settings for environment variables
    - Add health check endpoint `/health`
    - _Requirements: 1.2, 1.4_
  
  - [ ] 2.2 Implement Redis cache layer
    - Create `app/cache/redis.py` with async Redis client initialization
    - Implement `redis_cache` decorator with TTL and namespace support
    - Add cache key generation with MD5 hashing
    - Implement `invalidate_cache_pattern` function
    - _Requirements: 1.5, 2.4_
  
  - [ ] 2.3 Implement request ID middleware
    - Create `app/middleware/request_id.py` following pattern in `.kiro/steering/backend-patterns.md`
    - Generate or extract X-Request-ID header
    - Store in request.state for logging
    - Add X-Request-ID to response headers
    - _Requirements: 1.4, 3.4_
  
  - [ ] 2.4 Add CORS middleware and configure logging
    - Configure CORS with allowed origins from settings
    - Set up structured logging with request ID injection
    - Configure log levels and formatters
    - _Requirements: 1.4, 3.4_

- [ ] 3. Checkpoint - Verify FastAPI scaffold
  - Ensure FastAPI starts successfully with `uvicorn app.main:app --reload`
  - Verify health check endpoint returns 200
  - Verify Redis connection in logs
  - Ask the user if questions arise

- [ ] 4. Implement Jolpica REST routes (historical data)
  - [ ] 4.1 Create Pydantic models for standings
    - Create `app/models/common.py` with `DriverInfo`, `ConstructorInfo` base models
    - Create `app/models/standings.py` with `DriverStanding`, `ConstructorStanding` models
    - Add field validators for numeric strings
    - _Requirements: 1.3, 2.1_
  
  - [ ] 4.2 Implement standings router
    - Create `app/routers/standings.py` with 2 endpoints: `/api/standings/drivers/{year}`, `/api/standings/constructors/{year}`
    - Apply `@redis_cache` decorator with TTL 3600s
    - Call Jolpica service functions and return validated Pydantic models
    - Include router in `app/main.py`
    - _Requirements: 2.1, 2.4_
  
  - [ ]* 4.3 Write property test for standings endpoints
    - **Property 2: Position ordering**
    - **Validates: Requirements 2.1**
    - Test that standings positions are always sequential and unique
    - _Requirements: 4.2_
  
  - [ ] 4.4 Create Pydantic models for races
    - Create `app/models/races.py` with `Circuit`, `Race`, `RaceResult`, `RaceResultEntry`, `QualifyingResult`, `QualifyingResultEntry`, `LapTime` models
    - Add optional field handling for missing data
    - _Requirements: 1.3, 2.1_
  
  - [ ] 4.5 Implement races router
    - Create `app/routers/races.py` with 4 endpoints: `/api/races/{year}`, `/api/races/{year}/{round}/results`, `/api/races/{year}/{round}/qualifying`, `/api/races/{year}/{round}/laps`
    - Apply `@redis_cache` decorator with TTL 3600s
    - Call Jolpica service functions and return validated models
    - Include router in `app/main.py`
    - _Requirements: 2.1, 2.4_
  
  - [ ]* 4.6 Write unit tests for races endpoints
    - Test each endpoint with sample data
    - Test error handling for invalid year/round
    - Verify cache behavior
    - _Requirements: 4.1_

- [ ] 5. Checkpoint - Verify historical data endpoints
  - Test all Jolpica endpoints with curl or Postman
  - Verify cache hits in Redis using `redis-cli KEYS cache:*`
  - Verify response models match Pydantic schemas
  - Ask the user if questions arise

- [ ] 6. Implement analytics REST routes
  - [ ] 6.1 Create Pydantic models for analytics responses
    - Create `app/models/analytics.py` with models: `PerformanceTrend`, `ConsistencyScore`, `DNFRate`, `FormIndicator`, `DriverComparison`, `ChampionshipProjection`
    - Add field validators for score ranges (0-100) and rate ranges (0-1)
    - _Requirements: 1.3, 2.2_
  
  - [ ] 6.2 Implement analytics router - driver metrics
    - Create `app/routers/analytics.py` with endpoints: `/api/analytics/trends/{driver_id}/{year}`, `/api/analytics/consistency/{driver_id}/{year}`, `/api/analytics/form/{driver_id}/{year}`, `/api/analytics/dnf/{driver_id}/{year}`
    - Apply `@redis_cache` decorator with TTL 600s
    - Call analytics service functions
    - _Requirements: 2.2, 2.4_
  
  - [ ]* 6.3 Write property test for consistency score
    - **Property 1: Consistency score bounds**
    - **Validates: Requirements 2.2**
    - Test that consistency scores are always 0-100 for any valid race results
    - _Requirements: 4.2_
  
  - [ ] 6.4 Implement analytics router - comparative endpoints
    - Add endpoints: `/api/analytics/compare` (POST), `/api/analytics/circuit/{circuit_id}`, `/api/analytics/projection/{year}`
    - Handle multi-driver comparison request body
    - Generate Plotly-compatible chart data structures
    - _Requirements: 2.2, 2.3, 2.4_
  
  - [ ]* 6.5 Write unit tests for analytics endpoints
    - Test calculation accuracy against known Streamlit outputs
    - Test edge cases (no races, all DNFs, single race)
    - Verify Plotly data format
    - _Requirements: 4.1_

- [ ] 7. Checkpoint - Verify analytics endpoints
  - Test analytics endpoints with real driver IDs and years
  - Compare outputs to existing Streamlit calculations for accuracy
  - Verify cache behavior with 600s TTL
  - Ask the user if questions arise

- [ ] 8. Implement OpenF1 live data routes
  - [ ] 8.1 Extract OpenF1 service functions
    - Create `app/services/openf1.py` with 8 async functions: `fetch_current_session`, `fetch_session_drivers`, `fetch_live_positions`, `fetch_live_intervals`, `fetch_live_stints`, `fetch_live_pits`, `fetch_live_weather`, `fetch_live_racecontrol`
    - Use httpx.AsyncClient with OpenF1 base URL
    - Add error handling for API unavailability
    - _Requirements: 1.1, 2.5_
  
  - [ ] 8.2 Implement session mode determination logic
    - Create `app/services/live.py` with `determine_session_mode` function
    - Compare current UTC time to session start/end times
    - Return "live", "upcoming", or "replay" mode
    - Implement `aggregate_live_data` function to combine multiple OpenF1 calls
    - _Requirements: 2.5, 2.6_
  
  - [ ] 8.3 Create Pydantic models for live data
    - Create `app/models/live.py` with models: `SessionInfo`, `Position`, `Interval`, `RaceControlMessage`, `Weather`, `Stint`, `PitStop`
    - Add optional fields for missing live data
    - _Requirements: 1.3, 2.5_
  
  - [ ] 8.4 Implement live data router
    - Create `app/routers/live.py` with 9 endpoints: `/api/live/session`, `/api/live/drivers`, `/api/live/positions`, `/api/live/intervals`, `/api/live/stints`, `/api/live/pits`, `/api/live/weather`, `/api/live/racecontrol`, `/api/live/radio`
    - Do NOT cache live data (real-time requirement)
    - Include router in `app/main.py`
    - _Requirements: 2.5, 2.6_
  
  - [ ]* 8.5 Write unit tests for live endpoints
    - Test session mode determination logic with various timestamps
    - Test endpoint responses with mocked OpenF1 data
    - Test error handling when OpenF1 is unavailable
    - _Requirements: 4.1_

- [ ] 9. Implement WebSocket server for real-time updates
  - [ ] 9.1 Create WebSocket ConnectionManager
    - Create `app/ws/manager.py` with `ConnectionManager` class
    - Implement `connect`, `disconnect`, `broadcast` methods
    - Implement `_poll` method to fetch OpenF1 data every 4 seconds
    - Implement `_heartbeat` method for connection health checks
    - _Requirements: 2.6, 2.7_
  
  - [ ] 9.2 Implement WebSocket router
    - Create `app/routers/ws.py` with 2 WebSocket endpoints: `/ws/live/{session_key}`, `/ws/live`
    - Use ConnectionManager to handle connections
    - Broadcast updates with positions, intervals, race control messages
    - Handle client disconnections gracefully
    - Include router in `app/main.py`
    - _Requirements: 2.6, 2.7_
  
  - [ ]* 9.3 Write integration test for WebSocket
    - Test WebSocket connection and message reception
    - Test automatic polling starts/stops based on client count
    - Test heartbeat mechanism
    - _Requirements: 4.1_

- [ ] 10. Checkpoint - Verify backend completeness
  - Test all REST endpoints (22 total)
  - Test both WebSocket endpoints with a WebSocket client
  - Verify Redis caching with `redis-cli MONITOR`
  - Verify request ID propagation in logs
  - Ask the user if questions arise

- [ ] 11. Create React frontend scaffold
  - [ ] 11.1 Initialize React project with Vite
    - Run `npm create vite@latest frontend -- --template react-ts`
    - Install dependencies: react-router-dom, @tanstack/react-query, zustand, axios, plotly.js, react-plotly.js, tailwindcss, vitest, @testing-library/react, @testing-library/jest-dom, msw
    - Configure Tailwind CSS
    - _Requirements: 1.6, 1.7_
  
  - [ ] 11.2 Set up React Query and routing
    - Create `src/main.tsx` with QueryClientProvider configuration (5min staleTime, 10min gcTime, retry with exponential backoff)
    - Create `src/App.tsx` with React Router and 11 routes
    - Add lazy loading for all page components
    - _Requirements: 1.7, 2.8_
  
  - [ ] 11.3 Create API client and TypeScript types
    - Create `src/api/client.ts` with axios instance, base URL from env, request/response interceptors
    - Create `src/types/` with TypeScript interfaces matching backend Pydantic models: `standings.ts`, `races.ts`, `analytics.ts`, `live.ts`
    - _Requirements: 1.7, 2.8_
  
  - [ ] 11.4 Create Zustand stores
    - Create `src/store/liveRaceStore.ts` for live race state (positions, intervals, race control) - NO localStorage persistence
    - Create `src/store/sessionStore.ts` for session info and mode - NO localStorage persistence
    - Create `src/store/userPrefsStore.ts` with localStorage persistence for selected year, favorite drivers, theme
    - _Requirements: 2.8, 2.9_
  
  - [ ] 11.5 Create shared layout components
    - Create `src/components/layout/Layout.tsx` with header, sidebar, main content area, footer
    - Create `src/components/layout/Header.tsx` with logo, navigation, year selector
    - Create `src/components/shared/LoadingSpinner.tsx`, `ErrorMessage.tsx`, `DataTable.tsx`, `YearSelector.tsx`
    - _Requirements: 2.8_

- [ ] 12. Implement historical data pages (React)
  - [ ] 12.1 Create React Query hooks for historical data
    - Create `src/hooks/useStandings.ts` with `useDriverStandings`, `useConstructorStandings` hooks
    - Create `src/hooks/useRaces.ts` with `useRaceSchedule`, `useRaceResults`, `useQualifyingResults`, `useLapTimes` hooks
    - Configure query keys and staleTime appropriately
    - _Requirements: 2.8_
  
  - [ ] 12.2 Create Plotly chart components
    - Create `src/components/charts/HorizontalBarChart.tsx` for standings
    - Create `src/components/charts/LineChart.tsx` for championship progression
    - Create `src/components/charts/ScatterChart.tsx` for lap times
    - Create `src/components/charts/RadarChart.tsx` for driver comparison
    - Create `src/utils/constants.ts` with F1 color palette
    - _Requirements: 2.8, 2.9_
  
  - [ ] 12.3 Implement standings pages
    - Create `src/pages/DriverStandingsPage.tsx` with standings table and horizontal bar chart
    - Create `src/pages/ConstructorStandingsPage.tsx` with standings table and horizontal bar chart
    - Use `useDriverStandings` and `useConstructorStandings` hooks
    - Add loading and error states
    - _Requirements: 2.8, 2.9_
  
  - [ ] 12.4 Implement race pages
    - Create `src/pages/CalendarPage.tsx` with race schedule table
    - Create `src/pages/RacesPage.tsx` with race results table and fastest lap highlighting
    - Create `src/pages/QualifyingPage.tsx` with qualifying results and Q1/Q2/Q3 times
    - Create `src/pages/LapTimesPage.tsx` with lap time scatter chart
    - _Requirements: 2.8, 2.9_
  
  - [ ] 12.5 Implement overview and championship pages
    - Create `src/pages/OverviewPage.tsx` with next race card, latest results, standings preview
    - Create `src/pages/ChampionshipPage.tsx` with championship progression line chart
    - Create `src/pages/HeadToHeadPage.tsx` with driver selector and comparison table
    - _Requirements: 2.8, 2.9_
  
  - [ ]* 12.6 Write component tests for historical pages
    - Test DriverStandingsPage with MSW mocked API
    - Test loading and error states
    - Test chart rendering
    - _Requirements: 4.3_

- [ ] 13. Checkpoint - Verify historical pages
  - Start backend with `uvicorn app.main:app --reload`
  - Start frontend with `npm run dev`
  - Navigate through all historical pages and verify data loads correctly
  - Compare outputs to existing Streamlit app for accuracy
  - Ask the user if questions arise

- [ ] 14. Implement analytics page (React)
  - [ ] 14.1 Create React Query hooks for analytics
    - Create `src/hooks/useAnalytics.ts` with hooks: `usePerformanceTrends`, `useConsistencyScore`, `useFormIndicator`, `useDNFRate`, `useDriverComparison`, `useCircuitPerformance`, `useChampionshipProjection`
    - Configure 10-minute staleTime for analytics queries
    - _Requirements: 2.8_
  
  - [ ] 14.2 Create analytics page with tabs
    - Create `src/pages/AnalyticsPage.tsx` with tab navigation for 4 sections: Driver Analytics, Team Analytics, Circuit Analytics, Comparative Analytics
    - Create driver selector component
    - Add loading and error states for each section
    - _Requirements: 2.8, 2.9_
  
  - [ ] 14.3 Implement driver analytics section
    - Display performance trends line chart
    - Display consistency score with gauge visualization
    - Display form indicator with trend arrow
    - Display DNF rate with bar chart
    - _Requirements: 2.8, 2.9_
  
  - [ ] 14.4 Implement comparative analytics section
    - Create multi-driver selector (up to 5 drivers)
    - Display radar chart for multi-dimensional comparison
    - Display side-by-side metrics table
    - Display championship projection chart
    - _Requirements: 2.8, 2.9_
  
  - [ ]* 14.5 Write component tests for analytics page
    - Test analytics page with mocked API responses
    - Test tab navigation
    - Test driver selector
    - _Requirements: 4.3_

- [ ] 15. Implement live tracker page (React)
  - [ ] 15.1 Create WebSocket hook with reconnection
    - Create `src/hooks/useWebSocket.ts` following pattern in `.kiro/steering/frontend-patterns.md`
    - Implement exponential backoff reconnection (1s → 2s → 4s → 8s → 16s → 30s max)
    - Track connection status (connecting, connected, disconnected, error)
    - Handle ping/pong for heartbeat
    - _Requirements: 2.7, 2.9_
  
  - [ ] 15.2 Create live data hook combining REST and WebSocket
    - Create `src/hooks/useLiveData.ts` that fetches initial session info via REST
    - Subscribe to WebSocket for real-time updates
    - Update Zustand store with incoming data
    - Handle session mode changes (live → replay)
    - _Requirements: 2.7, 2.8, 2.9_
  
  - [ ] 15.3 Create live tracker components
    - Create `src/components/live/SessionModeIndicator.tsx` with color-coded mode badge
    - Create `src/components/live/PositionTracker.tsx` with live position table and position change indicators
    - Create `src/components/live/IntervalDisplay.tsx` with gap to leader and interval columns
    - Create `src/components/live/RaceControlFeed.tsx` with scrolling message feed
    - Create `src/components/live/WeatherWidget.tsx` with temperature, humidity, wind display
    - _Requirements: 2.9_
  
  - [ ] 15.4 Implement live tracker page
    - Create `src/pages/LiveTrackerPage.tsx` with grid layout for all live components
    - Use `useLiveData` hook to fetch and subscribe to updates
    - Display session info and mode indicator
    - Handle "upcoming" mode with countdown timer
    - Handle "replay" mode with historical data
    - _Requirements: 2.7, 2.9_
  
  - [ ]* 15.5 Write integration test for WebSocket hook
    - Test WebSocket connection and reconnection logic
    - Test exponential backoff timing
    - Test message parsing and state updates
    - _Requirements: 4.3_

- [ ] 16. Checkpoint - Verify frontend completeness
  - Test all 11 pages in the React app
  - Verify live tracker connects to WebSocket and receives updates
  - Verify all charts render correctly with Plotly
  - Verify year selector updates all pages
  - Ask the user if questions arise

- [ ] 17. Docker containerization and Nginx configuration
  - [ ] 17.1 Create backend Dockerfile
    - Create `backend/Dockerfile` with multi-stage build (builder + runtime)
    - Use python:3.11-slim base image
    - Install dependencies and copy application code
    - Expose port 8000
    - Set CMD to run uvicorn
    - _Requirements: 3.1, 3.2_
  
  - [ ] 17.2 Create frontend Dockerfile
    - Create `frontend/Dockerfile` with multi-stage build (build + nginx)
    - Use node:20-alpine for build stage
    - Use nginx:alpine for runtime stage
    - Copy Vite build output to nginx html directory
    - Copy nginx configuration
    - Expose port 80
    - _Requirements: 3.1, 3.2_
  
  - [ ] 17.3 Create Nginx configuration
    - Create `nginx/nginx.conf` with reverse proxy rules
    - Route `/api/*` to backend:8000
    - Route `/ws/*` to backend:8000 with WebSocket upgrade headers
    - Route `/*` to frontend static files
    - Enable gzip compression
    - Add rate limiting for API endpoints
    - _Requirements: 3.2, 3.3_
  
  - [ ] 17.4 Create Docker Compose configuration
    - Create `docker-compose.yml` with 4 services: nginx, frontend, backend, redis
    - Configure service dependencies (backend depends on redis)
    - Set up networks for service communication
    - Configure environment variables
    - Add health checks for all services
    - _Requirements: 3.1, 3.2_
  
  - [ ] 17.5 Create Docker Compose profiles for dev/prod
    - Add `docker-compose.dev.yml` with volume mounts for hot reload
    - Add `docker-compose.prod.yml` with optimized settings
    - Create `.env.example` files for both environments
    - _Requirements: 3.1_

- [ ] 18. Testing and final polish
  - [ ] 18.1 Run backend property-based tests
    - Execute all Hypothesis tests in `tests/test_analytics_properties.py`
    - Verify Property 1 (consistency score bounds) passes
    - Verify Property 2 (position ordering) passes
    - Fix any discovered edge cases
    - _Requirements: 4.2_
  
  - [ ] 18.2 Run frontend component tests
    - Execute Vitest tests with `npm run test`
    - Verify all component tests pass
    - Verify MSW handlers work correctly
    - _Requirements: 4.3_
  
  - [ ] 18.3 Perform end-to-end validation
    - Start all services with `docker-compose up`
    - Test all 11 frontend pages
    - Test all 22 REST endpoints
    - Test both WebSocket endpoints
    - Verify Redis caching reduces API calls
    - _Requirements: 4.1, 4.3_
  
  - [ ] 18.4 Create deployment documentation
    - Create `README.md` with setup instructions
    - Document environment variables
    - Document Docker commands for dev and prod
    - Add troubleshooting section
    - _Requirements: 3.4_
  
  - [ ] 18.5 Performance optimization
    - Verify Redis cache hit rates with `redis-cli INFO stats`
    - Optimize React Query staleTime settings
    - Add React.memo to expensive components
    - Verify Nginx gzip compression is working
    - _Requirements: 2.4, 3.3_

- [ ] 19. Final checkpoint - Production readiness
  - Verify all tests pass (backend + frontend)
  - Verify Docker Compose starts all services successfully
  - Verify feature parity with original Streamlit app
  - Verify logging and monitoring are configured
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements from `requirements.md` for traceability
- Checkpoints ensure incremental validation and provide opportunities for user feedback
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The migration follows a bottom-up approach: services → API → frontend
- All context documents (requirements.md, design.md, steering files) are available during implementation
- Backend uses Python 3.11+ with FastAPI, frontend uses TypeScript with React 18
- Redis caching reduces external API load by 80%+ for historical data
- WebSocket polling interval is 4 seconds for live data updates
- The implementation preserves all existing Streamlit functionality with identical outputs
