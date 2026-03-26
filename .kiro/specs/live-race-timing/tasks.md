# Implementation Plan: Live Race Timing Feature

## Overview

This implementation plan breaks down the Live Race Timing feature into discrete coding tasks. The feature implements a real-time race monitoring page with three operating modes (live, upcoming, replay), WebSocket-based live updates, and seven interactive panels. The implementation follows a bottom-up approach: backend infrastructure first, then state management, then UI components, with incremental validation at each checkpoint.

## Tasks

- [x] 1. Set up backend OpenF1 API client and session mode detection
  - Create `backend/app/services/openf1.py` with async HTTP client for OpenF1 API
  - Implement functions: `fetch_current_session()`, `fetch_live_positions()`, `fetch_live_intervals()`, `fetch_live_stints()`, `fetch_live_pits()`, `fetch_live_weather()`, `fetch_live_racecontrol()`, `fetch_live_radio()`, `fetch_sessions_by_year()`, `fetch_starting_grid()`
  - Create `backend/app/services/live.py` with `determine_session_mode()` function
  - Create `backend/app/models/live.py` with Pydantic models: SessionInfo, Position, Interval, Stint, PitStop, Weather, RaceControlMessage, TeamRadio, Driver
  - Use httpx.AsyncClient with connection pooling (max_keepalive_connections=20)
  - _Requirements: 1.1, 1.2, 4.2, 4.5-4.10, 22.1_

- [x] 1.1 Write unit tests for OpenF1 client and mode detection
  - Test `determine_session_mode()` returns "live" when current time is between date_start and date_end
  - Test `determine_session_mode()` returns "upcoming" when current time is before date_start
  - Test `determine_session_mode()` returns "replay" when current time is after date_end
  - Test OpenF1 client handles API errors gracefully (timeouts, 404, 500)
  - _Requirements: 1.2, 16.1, 16.2_

- [x] 2. Implement backend REST endpoints for live data
  - [x] 2.1 Create `backend/app/routers/live.py` with REST endpoints
    - Implement `GET /api/live/session` endpoint returning SessionInfo with mode field
    - Implement `GET /api/live/sessions?year={year}` endpoint for session list
    - Implement `GET /api/live/positions/{session_key}` endpoint
    - Implement `GET /api/live/intervals/{session_key}` endpoint
    - Implement `GET /api/live/stints/{session_key}` endpoint
    - Implement `GET /api/live/pits/{session_key}` endpoint
    - Implement `GET /api/live/weather/{session_key}` endpoint
    - Implement `GET /api/live/race-control/{session_key}` endpoint
    - Implement `GET /api/live/radio/{session_key}` endpoint
    - Implement `GET /api/live/grid/{session_key}` endpoint
    - Add error handling: 404 for no session found, 500 for internal errors
    - Add request ID propagation for distributed tracing
    - _Requirements: 1.1, 4.2, 4.5-4.10, 16.1, 16.2, 16.5, 16.6, 19.1, 21.8, 22.1_

  - [x] 2.2 Write unit tests for REST endpoints
    - Test `/api/live/session` returns correct mode for live/upcoming/replay scenarios
    - Test `/api/live/session` returns 404 when no session available
    - Test `/api/live/session` returns 500 on OpenF1 API failure
    - Test all data endpoints return correct data structure
    - _Requirements: 16.1, 16.2, 16.3_

- [x] 3. Checkpoint - Verify backend REST endpoints
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement WebSocket infrastructure
  - [x] 4.1 Create WebSocket connection manager
    - Create `backend/app/ws/manager.py` with ConnectionManager class
    - Implement `connect()`, `disconnect()`, `broadcast()` methods
    - Implement `_poll()` method that fetches positions, intervals, race control every 4 seconds
    - Implement `_heartbeat()` method that sends ping every 30 seconds
    - Use asyncio.gather for parallel data fetching
    - Track connections per session_key, start/stop polling based on client count
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 10.10, 17.2_

  - [x] 4.2 Create WebSocket router
    - Create `backend/app/routers/ws.py` with WebSocket endpoint `/ws/live/{session_key}`
    - Validate session_key parameter (must be numeric string)
    - Accept WebSocket connection and register with ConnectionManager
    - Listen for pong messages from client
    - Handle WebSocketDisconnect and cleanup
    - _Requirements: 2.1, 2.6, 14.3_

  - [x] 4.3 Write WebSocket integration tests
    - Test WebSocket connection establishment
    - Test ping/pong heartbeat mechanism
    - Test multiple clients receive same updates
    - Test polling starts when first client connects and stops when last disconnects
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 5. Checkpoint - Verify WebSocket functionality
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Set up frontend state management and data fetching
  - [x] 6.1 Create TypeScript interfaces and Zustand store
    - Create `frontend/src/types/live.ts` with interfaces: SessionMode, SessionInfo, Position, Interval, Stint, PitStop, Weather, RaceControlMessage, TeamRadio, Driver, WebSocketMessage
    - Create `frontend/src/store/liveRaceStore.ts` with Zustand store
    - Implement store state: sessionInfo, drivers, positions, intervals, intervalHistory, stints, pitStops, weather, raceControl, isConnected, lastUpdate
    - Implement store actions: setSessionInfo, setDrivers, updatePositions, updateIntervals, appendIntervalHistory, updateStints, addPitStop, updateWeather, addRaceControlMessage, setConnectionStatus, clearLiveData
    - Enable TypeScript strict mode
    - _Requirements: 1.6, 15.1, 15.2, 15.3, 15.4, 24.1, 24.2, 24.3, 24.4, 24.5, 24.6, 24.7, 24.8_

  - [x] 6.2 Create API client and React Query hooks
    - Create `frontend/src/api/live.ts` with API client functions for all REST endpoints
    - Create `frontend/src/hooks/useLiveData.ts` with React Query hooks
    - Configure React Query: 30 second stale time for session data, no caching for live mode data, 3 retry attempts
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.7_

  - [x] 6.3 Create WebSocket hook
    - Create `frontend/src/hooks/useWebSocket.ts` with useWebSocket hook
    - Implement connection establishment when enabled=true
    - Implement exponential backoff reconnection: 1s → 2s → 4s → 8s → 16s → 30s max
    - Stop reconnecting after 10 failed attempts
    - Parse incoming messages and update Zustand store
    - Handle message types: "update", "ping", "error"
    - Respond to ping with pong message
    - Validate message structure before updating state
    - Close connection when enabled=false or component unmounts
    - _Requirements: 2.1, 2.6, 2.7, 2.8, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 23.1, 23.2, 23.3, 23.4, 23.5, 23.6, 23.7, 23.8, 23.9_

  - [x] 6.4 Write property test for exponential backoff
    - **Property 7: Exponential Backoff Correctness**
    - **Validates: Requirements 2.7, 23.1-23.4**
    - Test that delay for attempt N equals min(1000 × 2^(N-1), 30000) milliseconds
    - Use fast-check to generate random attempt numbers 0-20
    - Verify calculated delay matches expected formula

- [x] 7. Checkpoint - Verify state management and data fetching
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement main page component and mode detection
  - [x] 8.1 Create LiveTrackerPage component
    - Create `frontend/src/pages/LiveTrackerPage.tsx` with main page component
    - Use React Query to fetch session info from `/api/live/session`
    - Update Zustand store with session info when data arrives
    - Connect WebSocket when mode is "live"
    - Implement polling: refetch session info every 30 seconds in upcoming mode
    - Clear live data on component unmount
    - Render LoadingSpinner while loading
    - Render ErrorMessage on error with retry button
    - Render mode-specific content based on sessionInfo.mode
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 1.7, 2.1, 2.8, 3.6, 3.7, 16.7, 16.8, 18.5, 18.6_

  - [x] 8.2 Write property test for session mode determinism
    - **Property 1: Session Mode Determinism**
    - **Validates: Requirements 1.2**
    - Test that calling determine_session_mode multiple times with same session data returns same mode
    - Use fast-check to generate random session start/end times
    - Verify mode determination is consistent across multiple calls

  - [x] 8.3 Write property test for mode-appropriate UI rendering
    - **Property 2: Mode-Appropriate UI Rendering**
    - **Validates: Requirements 1.3, 1.4, 1.5**
    - Test that live mode renders all 7 panels
    - Test that upcoming mode renders countdown/circuit/grid components
    - Test that replay mode renders session selector plus all 7 panels
    - Use React Testing Library to verify component presence

- [x] 9. Implement ModeBadge component
  - Create `frontend/src/components/live/ModeBadge.tsx`
  - Display red pill with pulsing dot and "LIVE" text for live mode
  - Display amber pill with "UPCOMING" text for upcoming mode
  - Display blue pill with "REPLAY — {circuit_name} {year}" text for replay mode
  - Position badge at top-right with sticky positioning
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 25.8_

- [x] 10. Implement Race Tower panel
  - [x] 10.1 Create RaceTower component
    - Create `frontend/src/components/live/RaceTower.tsx`
    - Subscribe to positions, intervals, drivers, stints from Zustand store
    - Merge position, interval, driver, and stint data for each driver
    - Sort drivers by position (P1-P20)
    - Display driver number, name, team with team color background
    - Display gap to leader (show "—" for P1, preserve "+1 LAP" format for lapped cars)
    - Display interval to car ahead (show "—" for P1)
    - Display current tire compound with colored indicator
    - Display tire age in laps
    - Use React.memo for performance optimization
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.9, 15.5, 17.3_

  - [x] 10.2 Write property test for position ordering
    - **Property 11: Position Ordering Invariant**
    - **Validates: Requirements 6.1**
    - Test that Race Tower displays drivers in ascending order by position number
    - Use fast-check to generate random position arrays
    - Verify rendered order matches sorted position values

  - [x] 10.3 Write property test for complete driver information
    - **Property 10: Complete Driver Information Display**
    - **Validates: Requirements 6.2-6.6**
    - Test that all required fields are present for each driver
    - Verify driver number, name, team, gap, interval, tire compound, tire age are all rendered
    - Use React Testing Library to check DOM for required elements

- [x] 11. Implement Gap Tracker Chart panel
  - Create `frontend/src/components/live/GapTrackerChart.tsx`
  - Subscribe to positions and drivers from Zustand store
  - Group positions by driver and calculate gap progression over laps
  - Create Plotly line chart with lap number on x-axis, gap to leader on y-axis
  - Use team colors for each driver's line
  - Display driver name and current gap on hover
  - Include legend with driver names and team colors
  - Support zoom and pan interactions
  - Use React.memo and Plotly streaming mode for performance
  - Adjust height based on viewport: 300px mobile, 350px tablet, 400px desktop
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 13.5, 15.6, 17.2, 17.3_

- [x] 12. Implement Tyre Strategy panel
  - Create `frontend/src/components/live/TyreStrategyPanel.tsx`
  - Subscribe to stints and drivers from Zustand store
  - Display horizontal stint bars for all 20 drivers
  - Use compound colors: SOFT=#E8002D, MEDIUM=#FFF200, HARD=#CCCCCC, INTERMEDIATE=#43B02A, WET=#0067AD
  - Display driver name acronym on left
  - Calculate stint length (lap_end - lap_start + 1)
  - Display stint length and tire age on hover tooltip
  - Align stint bars to lap numbers on x-axis
  - Enable horizontal scroll on mobile
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 13.7, 15.7_

- [x] 13. Implement Pit Stop List panel
  - [x] 13.1 Create PitStopList component
    - Create `frontend/src/components/live/PitStopList.tsx`
    - Subscribe to pitStops and drivers from Zustand store
    - Sort pit stops by duration to calculate rankings
    - Display pit stops in chronological order (most recent first)
    - Display driver name, lap number, pit duration, rank for each stop
    - Highlight fastest pit stop with green background
    - Highlight slowest pit stop with red background
    - Display total pit stops count in panel header
    - Support scrolling when more than 10 pit stops exist
    - Use virtual scrolling (react-window) when more than 50 pit stops
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 15.8, 17.4_

  - [x] 13.2 Write property test for pit stop ranking
    - **Property 12: Pit Stop Ranking Consistency**
    - **Validates: Requirements 9.4, 9.5, 9.6**
    - Test that pit stop with shortest duration is always ranked #1
    - Test that for any two pit stops A and B, if duration(A) < duration(B), then rank(A) < rank(B)
    - Use fast-check to generate random pit stop arrays

- [x] 14. Implement Weather panel
  - [x] 14.1 Create WeatherPanel component
    - Create `frontend/src/components/live/WeatherPanel.tsx`
    - Subscribe to weather from Zustand store
    - Display track temperature, air temperature, humidity, pressure, rainfall, wind direction, wind speed
    - Use weather icons for visual representation
    - Highlight rainfall indicator with blue background when rainfall=1
    - Display "No weather data available" when weather is null
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 15.9_

  - [x] 14.2 Write property test for weather data completeness
    - **Property 13: Weather Data Completeness**
    - **Validates: Requirements 10.1-10.7**
    - Test that all seven required fields are displayed when weather data exists
    - Verify track temp, air temp, humidity, pressure, rainfall, wind direction, wind speed are all rendered
    - Use React Testing Library to check DOM for required elements

- [x] 15. Implement Race Control Feed panel
  - [x] 15.1 Create RaceControlFeed component
    - Create `frontend/src/components/live/RaceControlFeed.tsx`
    - Subscribe to raceControl from Zustand store
    - Display messages in reverse chronological order (most recent first)
    - Display timestamp, category, message text, lap number for each message
    - Display flag icons: YELLOW=🟨, RED=🟥, GREEN=🟩, BLUE=🟦, CHEQUERED=🏁
    - Highlight safety car messages with yellow background
    - Highlight red flag messages with red background
    - Highlight DRS messages with green background
    - Support scrolling when more than 15 messages exist
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8, 11.9, 11.11, 15.10_

  - [x] 15.2 Write property test for race control message ordering
    - **Property 14: Race Control Message Ordering**
    - **Validates: Requirements 11.1**
    - Test that messages are displayed in reverse chronological order
    - Use fast-check to generate random message arrays with timestamps
    - Verify rendered order matches reverse chronological sort

- [x] 16. Implement Team Radio Player panel
  - Create `frontend/src/components/live/TeamRadioPlayer.tsx`
  - Subscribe to team radio clips from API endpoint
  - Display list of radio clips with driver name, lap number, duration
  - Implement HTML5 audio player with play, pause, seek, volume controls
  - Display waveform visualization during playback (optional enhancement)
  - Support filtering by driver
  - Support sorting by timestamp or driver
  - Add notification when new radio clip arrives in live mode
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 17.5_

- [x] 17. Checkpoint - Verify all live mode panels
  - Ensure all tests pass, ask the user if questions arise.

- [x] 18. Implement upcoming mode components
  - [x] 18.1 Create CountdownTimer component
    - Create `frontend/src/components/live/CountdownTimer.tsx`
    - Calculate time difference between current time and session start time
    - Display days, hours, minutes, seconds remaining
    - Update every second using setInterval
    - Highlight in red when time remaining < 1 hour
    - Add pulsing animation when time remaining < 5 minutes
    - Display "Session starting..." when countdown reaches zero
    - Handle timezone conversion correctly
    - _Requirements: 3.1, 3.7, 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.8_

  - [x] 18.2 Write property test for countdown timer accuracy
    - **Property 18: Countdown Timer Accuracy**
    - **Validates: Requirements 19.1, 19.2, 19.3**
    - Test that displayed time matches calculated difference between current time and start time
    - Verify accuracy within ±1 second
    - Use fast-check to generate random future timestamps

  - [x] 18.3 Create CircuitInfo component
    - Create `frontend/src/components/live/CircuitInfo.tsx`
    - Display circuit name, location (city and country), circuit length, number of laps, race distance
    - Display circuit image or map when available
    - Display lap record with driver name and time
    - Display number of DRS zones
    - Fetch circuit data from SessionInfo response
    - _Requirements: 3.2, 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9_

  - [x] 18.4 Create StartingGrid component
    - Create `frontend/src/components/live/StartingGrid.tsx`
    - Fetch starting grid from `/api/live/grid/{session_key}` endpoint
    - Display positions P1-P20 in grid formation
    - Display driver number, name, team, qualifying time for each position
    - Use team colors for driver backgrounds
    - Highlight pole position with gold border
    - Display grid penalties with indicator icon
    - Show original qualifying position and final grid position when penalty exists
    - Display "Grid not available" when data is missing
    - _Requirements: 3.3, 21.1, 21.2, 21.3, 21.4, 21.5, 21.6, 21.7, 21.8, 21.9_

- [ ] 19. Implement replay mode components
  - [ ] 19.1 Create SessionSelector component
    - Create `frontend/src/components/live/SessionSelector.tsx`
    - Fetch list of sessions from `/api/live/sessions?year={year}` endpoint
    - Display sessions grouped by year in descending order
    - Display sessions grouped by circuit within each year
    - Display session name, date, session type for each session
    - Implement search functionality to filter by circuit name
    - Implement filter by session type (race, qualifying, practice)
    - Update URL with session_key parameter when user selects session
    - Highlight currently selected session
    - Support keyboard navigation for accessibility
    - _Requirements: 4.1, 4.2, 4.3, 22.1, 22.2, 22.3, 22.4, 22.5, 22.6, 22.7, 22.8, 22.9_

  - [~] 19.2 Write property test for session grouping
    - **Property 9: Session Grouping Correctness**
    - **Validates: Requirements 4.2, 22.2, 22.3**
    - Test that sessions are grouped by year (descending) then by circuit
    - Test that sessions from same year and circuit appear together
    - Use fast-check to generate random session arrays

  - [~] 19.3 Implement replay mode data fetching
    - When user selects session in SessionSelector, fetch all panel data in parallel
    - Use React Query to fetch: positions, intervals, stints, pits, weather, race-control
    - Update Zustand store with fetched data
    - Display loading spinner while fetching
    - Display error message for failed requests
    - _Requirements: 4.3, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 16.5_

- [~] 20. Checkpoint - Verify upcoming and replay modes
  - Ensure all tests pass, ask the user if questions arise.

- [~] 21. Implement responsive layout and styling
  - Apply Tailwind CSS responsive grid classes to LiveTrackerPage
  - Mobile (<768px): Single column layout, all panels full width
  - Tablet (768px-1023px): 2-column grid, Race Tower full width
  - Desktop (≥1024px): 3-column grid, Race Tower full width, Gap Tracker 2 cols, Weather 1 col
  - Adjust chart heights: 300px mobile, 350px tablet, 400px desktop
  - Ensure touch targets are minimum 44x44px on mobile
  - Disable hover interactions on touch devices
  - Enable horizontal scroll for Tyre Strategy on mobile
  - Optimize font sizes for mobile readability
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8, 13.9_

- [~] 22. Implement error handling and recovery
  - Add error boundary component to catch React rendering errors
  - Display fallback UI with reload button when error boundary catches error
  - Display "No active session" message when session API returns 404
  - Display "Server error" message when session API returns 500, retry after 10 seconds
  - Display "Connection failed" message when WebSocket fails to establish
  - Display "Reconnecting... (attempt N)" message during reconnection attempts
  - Display "Connected" message for 2 seconds after successful reconnection
  - Display manual reconnect button after 10 consecutive failed reconnection attempts
  - Display "Data source unavailable" message when OpenF1 API is unavailable
  - Log all errors to console in development mode
  - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.9, 23.5, 23.6, 23.7, 23.8_

- [~] 23. Implement performance optimizations
  - Wrap RaceTower, GapTrackerChart, TyreStrategyPanel, PitStopList, WeatherPanel, RaceControlFeed with React.memo
  - Implement debouncing for WebSocket updates (250ms minimum interval, max 4 updates/second)
  - Use Plotly streaming mode for Gap Tracker Chart updates
  - Implement virtual scrolling for PitStopList when more than 50 entries
  - Lazy load TeamRadioPlayer audio files on demand
  - Implement code splitting for panel components using React.lazy
  - Prefetch session API data during page load
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.9_

- [~] 23.1 Write property test for WebSocket message timestamp ordering
  - **Property 16: WebSocket Message Timestamp Ordering**
  - **Validates: Requirements 14.8**
  - Test that application displays data from message with most recent timestamp
  - Test that out-of-order messages don't cause older data to overwrite newer data
  - Use fast-check to generate random message sequences with timestamps

- [~] 23.2 Write property test for performance latency
  - **Property 20: Performance Latency Bound**
  - **Validates: Requirements 17.9**
  - Measure time from WebSocket message receipt to DOM update completion
  - Verify p95 latency is under 100ms
  - Run 100 iterations and calculate 95th percentile

- [~] 24. Implement accessibility features
  - Use semantic HTML elements for all panels (section, article, nav)
  - Add ARIA labels for all interactive elements
  - Support keyboard navigation for all controls (Tab, Enter, Space, Arrow keys)
  - Add focus indicators for keyboard navigation (outline, ring classes)
  - Ensure color contrast ratios meet WCAG AA minimum (4.5:1 for text)
  - Provide text alternatives for visual information (alt text, aria-label)
  - Use ARIA live regions for announcing live updates to screen readers
  - Add appropriate ARIA role and label for ModeBadge
  - Provide keyboard controls for TeamRadioPlayer audio playback
  - Support keyboard navigation for SessionSelector
  - _Requirements: 22.9, 25.1, 25.2, 25.3, 25.4, 25.5, 25.6, 25.7, 25.8, 25.9_

- [~] 25. Final checkpoint - Integration testing and polish
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Implementation uses TypeScript for frontend and Python for backend
- Frontend uses React 18, Zustand, React Query, Plotly.js, Tailwind CSS
- Backend uses FastAPI, Pydantic, httpx, WebSocket support via Starlette
