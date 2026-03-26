# Requirements Document: Live Race Timing Feature

## Introduction

This document specifies the requirements for the Live Race Timing feature, the flagship page of the F1 FastAPI dashboard application. The Live Race Tracker provides real-time race monitoring with automatic mode detection, WebSocket-based live updates, and comprehensive telemetry visualization across seven interactive panels. The feature supports three distinct operating modes (live, upcoming, replay) and automatically determines which mode to display based on session status.

## Glossary

- **Live_Tracker_Page**: The React component rendered at /live that displays real-time race information
- **Session_Mode**: Operating mode determining data source and UI behavior ("live", "upcoming", or "replay")
- **Session_API**: REST endpoint at /api/live/session that returns current session information and mode
- **WebSocket_Connection**: Real-time bidirectional communication channel at /ws/live/{session_key}
- **Race_Tower**: Panel displaying P1-P20 driver positions with gaps, intervals, and tire information
- **Gap_Tracker_Chart**: Plotly line chart showing gap to leader over laps for all drivers
- **Tyre_Strategy_Panel**: Visual representation of tire stint bars for all 20 drivers
- **Pit_Stop_List**: Live log of pit stops with duration rankings
- **Weather_Panel**: Display of track temperature, air temperature, humidity, rainfall, wind data
- **Race_Control_Feed**: Event log showing flags, safety car deployments, and DRS status
- **Team_Radio_Player**: Audio player for driver radio communications
- **Mode_Badge**: Visual indicator showing current session mode with appropriate styling
- **OpenF1_API**: External API providing real-time F1 telemetry data
- **Zustand_Store**: State management solution for React application state
- **Countdown_Timer**: Component displaying time remaining until session start
- **Starting_Grid**: Display of driver starting positions for upcoming race
- **Session_Selector**: UI component allowing user to select past sessions for replay
- **Exponential_Backoff**: Reconnection strategy with increasing delay between attempts
- **Circuit_Info**: Display of circuit name, location, and track characteristics

## Requirements

### Requirement 1: Session Mode Detection

**User Story:** As a user, I want the application to automatically detect the current session mode, so that I see the appropriate interface without manual configuration.

#### Acceptance Criteria

1. WHEN Live_Tracker_Page loads, THE Live_Tracker_Page SHALL call GET /api/live/session
2. THE Session_API SHALL return a response including mode field with value "live", "upcoming", or "replay"
3. WHEN mode is "live", THE Live_Tracker_Page SHALL display all 7 panels with real-time data
4. WHEN mode is "upcoming", THE Live_Tracker_Page SHALL display Circuit_Info, Countdown_Timer, and Starting_Grid
5. WHEN mode is "replay", THE Live_Tracker_Page SHALL display Session_Selector and all 7 panels with historical data
6. THE Live_Tracker_Page SHALL store Session_Mode in Zustand_Store for access by child components
7. WHEN Session_API returns an error, THE Live_Tracker_Page SHALL display an error message and retry after 10 seconds

### Requirement 2: Live Mode WebSocket Connection

**User Story:** As a user watching a live race, I want real-time updates without refreshing the page, so that I can follow the race seamlessly.

#### Acceptance Criteria

1. WHEN Session_Mode is "live", THE Live_Tracker_Page SHALL connect to /ws/live/{session_key}
2. THE WebSocket_Connection SHALL send initial session state immediately after connection
3. WHILE WebSocket_Connection is open, THE WebSocket_Connection SHALL push position updates every 4 seconds
4. WHILE WebSocket_Connection is open, THE WebSocket_Connection SHALL push interval updates every 4 seconds
5. WHILE WebSocket_Connection is open, THE WebSocket_Connection SHALL push race control messages immediately when they occur
6. WHEN WebSocket_Connection closes unexpectedly, THE Live_Tracker_Page SHALL attempt reconnection with Exponential_Backoff
7. THE Exponential_Backoff SHALL start with 1 second delay and double on each attempt up to maximum 30 seconds
8. WHEN Session_Mode changes from "live" to another mode, THE Live_Tracker_Page SHALL close WebSocket_Connection

### Requirement 3: Upcoming Mode Display

**User Story:** As a user before a race starts, I want to see countdown and starting grid information, so that I can prepare for the upcoming session.

#### Acceptance Criteria

1. WHEN Session_Mode is "upcoming", THE Live_Tracker_Page SHALL display Countdown_Timer showing time until session start
2. WHEN Session_Mode is "upcoming", THE Live_Tracker_Page SHALL display Circuit_Info including circuit name, location, and lap count
3. WHEN Session_Mode is "upcoming", THE Live_Tracker_Page SHALL display Starting_Grid with driver positions P1-P20
4. WHEN Session_Mode is "upcoming", THE Live_Tracker_Page SHALL display session schedule with practice, qualifying, and race times
5. WHEN Session_Mode is "upcoming", THE Live_Tracker_Page SHALL NOT establish WebSocket_Connection
6. WHEN Session_Mode is "upcoming", THE Live_Tracker_Page SHALL poll Session_API every 30 seconds to detect mode change
7. WHEN Countdown_Timer reaches zero, THE Live_Tracker_Page SHALL refresh Session_Mode

### Requirement 4: Replay Mode Session Selection

**User Story:** As a user reviewing past races, I want to select any historical session, so that I can analyze previous race data.

#### Acceptance Criteria

1. WHEN Session_Mode is "replay", THE Live_Tracker_Page SHALL display Session_Selector with list of past sessions
2. THE Session_Selector SHALL fetch list of available sessions from OpenF1 API at https://api.openf1.org/v1/sessions?year={year}
3. THE Session_Selector SHALL group sessions by year and circuit
4. WHEN user selects a session, THE Live_Tracker_Page SHALL load all panel data from REST endpoints
4. WHEN Session_Mode is "replay", THE Live_Tracker_Page SHALL NOT establish WebSocket_Connection
5. THE Live_Tracker_Page SHALL fetch positions from /api/live/positions/{selected_key}
6. THE Live_Tracker_Page SHALL fetch intervals from /api/live/intervals/{selected_key}
7. THE Live_Tracker_Page SHALL fetch race control from /api/live/race-control/{selected_key}
8. THE Live_Tracker_Page SHALL fetch weather from /api/live/weather/{selected_key}
9. THE Live_Tracker_Page SHALL fetch pit stops from /api/live/pits/{selected_key}
10. THE Live_Tracker_Page SHALL fetch tire stints from /api/live/stints/{selected_key}

### Requirement 5: Mode Badge Display

**User Story:** As a user, I want a clear visual indicator of the current mode, so that I understand what data I'm viewing.

#### Acceptance Criteria

1. WHEN Session_Mode is "live", THE Mode_Badge SHALL display red pill background with pulsing dot animation
2. WHEN Session_Mode is "live", THE Mode_Badge SHALL display text "LIVE" in white
3. WHEN Session_Mode is "upcoming", THE Mode_Badge SHALL display amber pill background without animation
4. WHEN Session_Mode is "upcoming", THE Mode_Badge SHALL display text "UPCOMING" in dark text
5. WHEN Session_Mode is "replay", THE Mode_Badge SHALL display blue pill background without animation
6. WHEN Session_Mode is "replay", THE Mode_Badge SHALL display text "REPLAY — {circuit_name} {year}"
7. THE Mode_Badge SHALL be positioned at top-right of Live_Tracker_Page
8. THE Mode_Badge SHALL remain visible during page scroll

### Requirement 6: Race Tower Panel

**User Story:** As a user, I want to see current race positions with timing data, so that I can understand the race order and gaps.

#### Acceptance Criteria

1. THE Race_Tower SHALL display positions P1 through P20 in vertical list
2. FOR EACH driver position, THE Race_Tower SHALL display driver number, driver name, and team
3. FOR EACH driver position except P1, THE Race_Tower SHALL display gap to leader in seconds (P1 displays '—', lapped cars display '+1 LAP' as-is) (P1 displays '—', lapped cars display '+1 LAP' as-is)
4. FOR EACH driver position except P1, THE Race_Tower SHALL display interval to car ahead in seconds
5. FOR EACH driver position, THE Race_Tower SHALL display current tire compound (SOFT, MEDIUM, HARD, INTERMEDIATE, WET)
6. FOR EACH driver position, THE Race_Tower SHALL display tire age in laps
7. WHEN position data updates, THE Race_Tower SHALL animate position changes with smooth transitions
8. WHEN a driver is in pit lane, THE Race_Tower SHALL display "IN PIT" indicator
9. THE Race_Tower SHALL use team colors for driver name background

### Requirement 7: Gap Tracker Chart Panel

**User Story:** As a user, I want to visualize gaps to the leader over time, so that I can see race pace trends and strategy impacts.

#### Acceptance Criteria

1. THE Gap_Tracker_Chart SHALL display a Plotly line chart with lap number on x-axis
2. THE Gap_Tracker_Chart SHALL display gap to leader in seconds on y-axis
3. FOR EACH driver, THE Gap_Tracker_Chart SHALL plot a line showing gap progression over laps
4. THE Gap_Tracker_Chart SHALL use team colors for each driver's line
5. THE Gap_Tracker_Chart SHALL display driver name and current gap on hover
6. THE Gap_Tracker_Chart SHALL update in real-time as new lap data arrives in live mode
7. THE Gap_Tracker_Chart SHALL include legend with driver names and team colors
8. THE Gap_Tracker_Chart SHALL support zoom and pan interactions
9. WHEN a driver retires, THE Gap_Tracker_Chart SHALL end their line at retirement lap

### Requirement 8: Tyre Strategy Panel

**User Story:** As a user, I want to see tire strategy for all drivers, so that I can understand pit stop strategies and tire management.

#### Acceptance Criteria

1. THE Tyre_Strategy_Panel SHALL display horizontal stint bars for all 20 drivers
2. FOR EACH driver, THE Tyre_Strategy_Panel SHALL display driver name and number on left
3. FOR EACH stint, THE Tyre_Strategy_Panel SHALL display colored bar representing tire compound
4. THE Tyre_Strategy_Panel SHALL use red (#E8002D) for SOFT, yellow (#FFF200) for MEDIUM, grey (#CCCCCC) for HARD compound
5. THE Tyre_Strategy_Panel SHALL use green for INTERMEDIATE, blue for WET compound
6. FOR EACH stint bar, THE Tyre_Strategy_Panel SHALL display stint length in laps
7. FOR EACH stint bar, THE Tyre_Strategy_Panel SHALL display tire age at stint start
8. THE Tyre_Strategy_Panel SHALL align stint bars to lap numbers on x-axis
9. WHEN a driver pits, THE Tyre_Strategy_Panel SHALL add new stint bar in real-time

### Requirement 9: Pit Stop List Panel

**User Story:** As a user, I want to see all pit stops with durations, so that I can compare pit stop performance.

#### Acceptance Criteria

1. THE Pit_Stop_List SHALL display all pit stops in chronological order with most recent first
2. FOR EACH pit stop, THE Pit_Stop_List SHALL display driver name, lap number, and pit duration
3. FOR EACH pit stop, THE Pit_Stop_List SHALL display tire compound fitted during stop
4. THE Pit_Stop_List SHALL highlight fastest pit stop with green background
5. THE Pit_Stop_List SHALL highlight slowest pit stop with red background
6. THE Pit_Stop_List SHALL display pit stop rank (1st fastest, 2nd fastest, etc.)
7. WHEN a new pit stop occurs in live mode, THE Pit_Stop_List SHALL add entry with animation
8. THE Pit_Stop_List SHALL support scrolling when more than 10 pit stops exist
9. THE Pit_Stop_List SHALL display total pit stops count at panel header

### Requirement 10: Weather Panel

**User Story:** As a user, I want to see current weather conditions, so that I can understand how weather affects race strategy.

#### Acceptance Criteria

1. THE Weather_Panel SHALL display track temperature in Celsius
2. THE Weather_Panel SHALL display air temperature in Celsius
3. THE Weather_Panel SHALL display humidity as percentage
4. THE Weather_Panel SHALL display atmospheric pressure in mbar
5. THE Weather_Panel SHALL display rainfall indicator (0 = dry, 1 = rain)
6. THE Weather_Panel SHALL display wind direction in degrees
7. THE Weather_Panel SHALL display wind speed in km/h
8. THE Weather_Panel SHALL use weather icons for visual representation
9. WHEN rainfall is detected, THE Weather_Panel SHALL highlight rainfall indicator with blue background
10. THE Weather_Panel SHALL update every 30 seconds in live mode

### Requirement 11: Race Control Feed Panel

**User Story:** As a user, I want to see race control messages and flags, so that I can understand race incidents and safety car periods.

#### Acceptance Criteria

1. THE Race_Control_Feed SHALL display all race control messages in chronological order with most recent first
2. FOR EACH message, THE Race_Control_Feed SHALL display timestamp, category, and message text
3. FOR EACH message with flag, THE Race_Control_Feed SHALL display flag icon (yellow, red, green, blue, checkered)
4. THE Race_Control_Feed SHALL highlight safety car messages with yellow background
5. THE Race_Control_Feed SHALL highlight red flag messages with red background
6. THE Race_Control_Feed SHALL highlight DRS enabled/disabled messages with green background
7. WHEN a new message arrives in live mode, THE Race_Control_Feed SHALL add entry with animation
8. THE Race_Control_Feed SHALL support scrolling when more than 15 messages exist
9. THE Race_Control_Feed SHALL display lap number for each message when available
10. THE Race_Control_Feed SHALL filter messages by category (flags, safety car, DRS, incidents)
11. THE Race_Control_Feed SHALL fetch messages from /api/live/race-control endpoint

### Requirement 12: Team Radio Player Panel

**User Story:** As a user, I want to listen to team radio communications, so that I can hear driver and team interactions.

#### Acceptance Criteria

1. THE Team_Radio_Player SHALL display list of available radio clips with driver name and timestamp
2. FOR EACH radio clip, THE Team_Radio_Player SHALL display driver name, lap number, and duration
3. WHEN user clicks a radio clip, THE Team_Radio_Player SHALL play audio using HTML5 audio element
4. THE Team_Radio_Player SHALL display playback controls (play, pause, seek, volume)
5. THE Team_Radio_Player SHALL display waveform visualization during playback
6. WHEN a new radio clip arrives in live mode, THE Team_Radio_Player SHALL add entry with notification
7. THE Team_Radio_Player SHALL support filtering by driver
8. THE Team_Radio_Player SHALL support sorting by timestamp or driver
9. THE Team_Radio_Player SHALL fetch radio clips from /api/live/radio endpoint

### Requirement 13: Responsive Layout

**User Story:** As a mobile user, I want the live tracker to work on my phone, so that I can follow races on any device.

#### Acceptance Criteria

1. WHEN viewport width is less than 768px, THE Live_Tracker_Page SHALL stack all panels vertically
2. WHEN viewport width is 768px or greater, THE Live_Tracker_Page SHALL display panels in 2-column grid
3. WHEN viewport width is 1024px or greater, THE Live_Tracker_Page SHALL display panels in 3-column grid
4. THE Race_Tower SHALL remain full-width on all viewport sizes
5. THE Gap_Tracker_Chart SHALL adjust height based on viewport size
6. THE Mode_Badge SHALL remain visible and positioned correctly on all viewport sizes
7. THE Live_Tracker_Page SHALL use touch-friendly tap targets on mobile (minimum 44x44px)
8. THE Live_Tracker_Page SHALL disable hover interactions on touch devices
9. THE Live_Tracker_Page SHALL optimize chart rendering for mobile performance

### Requirement 14: WebSocket Message Parsing

**User Story:** As a developer, I want robust WebSocket message parsing, so that real-time updates are correctly processed.

#### Acceptance Criteria

1. THE Live_Tracker_Page SHALL parse incoming WebSocket messages as JSON
2. WHEN message type is "update", THE Live_Tracker_Page SHALL extract positions, intervals, and race_control arrays
3. WHEN message type is "ping", THE Live_Tracker_Page SHALL respond with pong message
4. WHEN message type is "error", THE Live_Tracker_Page SHALL display error notification and close connection
5. WHEN message contains invalid JSON, THE Live_Tracker_Page SHALL log error and continue listening
6. THE Live_Tracker_Page SHALL validate message structure before updating state
7. WHEN message is missing required fields, THE Live_Tracker_Page SHALL log warning and skip update
8. THE Live_Tracker_Page SHALL handle out-of-order messages by comparing timestamps

### Requirement 15: State Management with Zustand

**User Story:** As a developer, I want centralized state management for live race data, so that all panels access consistent data.

#### Acceptance Criteria

1. THE Live_Tracker_Page SHALL use Zustand_Store for storing positions, intervals, stints, pits, weather, and race control data
2. THE Zustand_Store SHALL provide typed selectors for accessing each data type
3. THE Zustand_Store SHALL provide actions for updating positions, intervals, stints, pits, weather, and race control
4. WHEN WebSocket message arrives, THE Live_Tracker_Page SHALL update Zustand_Store using appropriate action
5. THE Race_Tower SHALL subscribe to positions and intervals from Zustand_Store
6. THE Gap_Tracker_Chart SHALL subscribe to positions from Zustand_Store
7. THE Tyre_Strategy_Panel SHALL subscribe to stints from Zustand_Store
8. THE Pit_Stop_List SHALL subscribe to pits from Zustand_Store
9. THE Weather_Panel SHALL subscribe to weather from Zustand_Store
10. THE Race_Control_Feed SHALL subscribe to race control from Zustand_Store

### Requirement 16: Error Handling and Recovery

**User Story:** As a user, I want the application to handle errors gracefully, so that temporary issues don't break my experience.

#### Acceptance Criteria

1. WHEN Session_API returns 404, THE Live_Tracker_Page SHALL display "No active session" message
2. WHEN Session_API returns 500, THE Live_Tracker_Page SHALL display "Server error" message and retry after 10 seconds
3. WHEN WebSocket_Connection fails to establish, THE Live_Tracker_Page SHALL display "Connection failed" message
4. WHEN WebSocket_Connection closes with error code, THE Live_Tracker_Page SHALL log error and attempt reconnection
5. WHEN REST endpoint returns error in replay mode, THE Live_Tracker_Page SHALL display error message for affected panel
6. WHEN OpenF1_API is unavailable, THE Live_Tracker_Page SHALL display "Data source unavailable" message
7. THE Live_Tracker_Page SHALL implement error boundary to catch React rendering errors
8. WHEN error boundary catches error, THE Live_Tracker_Page SHALL display fallback UI with reload button
9. THE Live_Tracker_Page SHALL log all errors to console in development mode

### Requirement 17: Performance Optimization

**User Story:** As a user, I want smooth performance during live updates, so that the interface remains responsive.

#### Acceptance Criteria

1. THE Live_Tracker_Page SHALL debounce WebSocket updates to maximum 4 updates per second
2. THE Gap_Tracker_Chart SHALL use Plotly's streaming mode for efficient updates
3. THE Race_Tower SHALL use React.memo to prevent unnecessary re-renders
4. THE Live_Tracker_Page SHALL use virtual scrolling for Pit_Stop_List when more than 50 entries exist
5. THE Live_Tracker_Page SHALL lazy load Team_Radio_Player audio files on demand
6. THE Live_Tracker_Page SHALL implement code splitting for panel components
7. THE Live_Tracker_Page SHALL prefetch Session_API data during page load
8. THE Live_Tracker_Page SHALL use Web Workers for heavy data processing if needed
9. THE Live_Tracker_Page SHALL achieve 60fps during live updates on desktop browsers

### Requirement 18: Data Fetching with React Query

**User Story:** As a developer, I want declarative data fetching for REST endpoints, so that loading and error states are handled automatically.

#### Acceptance Criteria

1. THE Live_Tracker_Page SHALL use React Query for fetching Session_API data
2. THE Live_Tracker_Page SHALL use React Query for fetching replay mode data
3. THE Live_Tracker_Page SHALL configure React Query with 30 second stale time for session data
4. THE Live_Tracker_Page SHALL configure React Query with no caching for live mode data
5. THE Live_Tracker_Page SHALL display loading spinner while React Query is fetching
6. THE Live_Tracker_Page SHALL display error message when React Query encounters error
7. THE Live_Tracker_Page SHALL implement retry logic with 3 attempts for failed requests
8. THE Live_Tracker_Page SHALL refetch session data on window focus in upcoming mode

### Requirement 19: Countdown Timer Implementation

**User Story:** As a user in upcoming mode, I want to see time remaining until race start, so that I know when to return.

#### Acceptance Criteria

1. THE Countdown_Timer SHALL calculate time difference between current time and session start time
2. THE Countdown_Timer SHALL display days, hours, minutes, and seconds remaining
3. THE Countdown_Timer SHALL update every second
4. WHEN time remaining is less than 1 hour, THE Countdown_Timer SHALL highlight in red
5. WHEN time remaining is less than 5 minutes, THE Countdown_Timer SHALL add pulsing animation
6. WHEN Countdown_Timer reaches zero, THE Countdown_Timer SHALL display "Session starting..." message
7. THE Countdown_Timer SHALL handle timezone conversion correctly
8. THE Countdown_Timer SHALL display session start time in user's local timezone

### Requirement 20: Circuit Information Display

**User Story:** As a user, I want to see circuit details, so that I understand the track characteristics.

#### Acceptance Criteria

1. THE Circuit_Info SHALL display circuit name
2. THE Circuit_Info SHALL display circuit location (city and country)
3. THE Circuit_Info SHALL display circuit length in kilometers
4. THE Circuit_Info SHALL display number of laps
5. THE Circuit_Info SHALL display race distance in kilometers
6. THE Circuit_Info SHALL display circuit image or map when available
7. THE Circuit_Info SHALL display lap record with driver name and time
8. THE Circuit_Info SHALL display number of DRS zones
9. THE Circuit_Info SHALL fetch circuit data from Session_API response

### Requirement 21: Starting Grid Display

**User Story:** As a user in upcoming mode, I want to see the starting grid, so that I know driver positions before the race.

#### Acceptance Criteria

1. THE Starting_Grid SHALL display positions P1 through P20 in grid formation
2. FOR EACH grid position, THE Starting_Grid SHALL display driver number, driver name, and team
3. FOR EACH grid position, THE Starting_Grid SHALL display qualifying time
4. THE Starting_Grid SHALL use team colors for driver backgrounds
5. THE Starting_Grid SHALL highlight pole position with gold border
6. THE Starting_Grid SHALL display grid penalties with indicator icon
7. WHEN driver has grid penalty, THE Starting_Grid SHALL show original qualifying position and final grid position
8. THE Starting_Grid SHALL fetch starting grid from /api/live/grid/{session_key} endpoint
9. THE Starting_Grid SHALL display "Grid not available" message when data is missing

### Requirement 22: Session Selector Implementation

**User Story:** As a user in replay mode, I want to easily select past sessions, so that I can review historical races.

#### Acceptance Criteria

1. THE Session_Selector SHALL fetch list of available sessions from OpenF1 API at https://api.openf1.org/v1/sessions?year={year}
2. THE Session_Selector SHALL display sessions grouped by year in descending order
3. THE Session_Selector SHALL display sessions grouped by circuit within each year
4. FOR EACH session, THE Session_Selector SHALL display session name, date, and session type
5. THE Session_Selector SHALL implement search functionality to filter sessions by circuit name
6. THE Session_Selector SHALL implement filter by session type (race, qualifying, practice)
7. WHEN user selects a session, THE Session_Selector SHALL update URL with session_key parameter
8. THE Session_Selector SHALL highlight currently selected session
9. THE Session_Selector SHALL support keyboard navigation for accessibility

### Requirement 23: WebSocket Reconnection Strategy

**User Story:** As a user, I want automatic reconnection when connection drops, so that I don't miss race updates.

#### Acceptance Criteria

1. WHEN WebSocket_Connection closes unexpectedly, THE Live_Tracker_Page SHALL attempt reconnection after 1 second
2. WHEN first reconnection fails, THE Live_Tracker_Page SHALL attempt reconnection after 2 seconds
3. WHEN second reconnection fails, THE Live_Tracker_Page SHALL attempt reconnection after 4 seconds
4. THE Live_Tracker_Page SHALL continue doubling delay up to maximum 30 seconds between attempts
5. THE Live_Tracker_Page SHALL display "Reconnecting..." message during reconnection attempts
6. THE Live_Tracker_Page SHALL display reconnection attempt count (e.g., "Reconnecting... (attempt 3)")
7. WHEN reconnection succeeds, THE Live_Tracker_Page SHALL display "Connected" message for 2 seconds
8. WHEN 10 consecutive reconnection attempts fail, THE Live_Tracker_Page SHALL stop attempting and display manual reconnect button
9. THE Live_Tracker_Page SHALL reset reconnection delay to 1 second after successful connection

### Requirement 24: TypeScript Type Safety

**User Story:** As a developer, I want strong typing for all data structures, so that type errors are caught at compile time.

#### Acceptance Criteria

1. THE Live_Tracker_Page SHALL define TypeScript interfaces for Position, Interval, Stint, PitStop, Weather, and RaceControl types
2. THE Live_Tracker_Page SHALL define TypeScript interface for SessionInfo type
3. THE Live_Tracker_Page SHALL define TypeScript interface for WebSocket message types
4. THE Live_Tracker_Page SHALL use TypeScript generics for Zustand_Store state and actions
5. THE Live_Tracker_Page SHALL use TypeScript for all React component props
6. THE Live_Tracker_Page SHALL enable strict mode in TypeScript configuration
7. THE Live_Tracker_Page SHALL have zero TypeScript errors in production build
8. THE Live_Tracker_Page SHALL use discriminated unions for Session_Mode type

### Requirement 25: Accessibility Compliance

**User Story:** As a user with disabilities, I want the live tracker to be accessible, so that I can follow races using assistive technologies.

#### Acceptance Criteria

1. THE Live_Tracker_Page SHALL use semantic HTML elements for all panels
2. THE Live_Tracker_Page SHALL provide ARIA labels for all interactive elements
3. THE Live_Tracker_Page SHALL support keyboard navigation for all controls
4. THE Live_Tracker_Page SHALL provide focus indicators for keyboard navigation
5. THE Live_Tracker_Page SHALL use sufficient color contrast ratios (WCAG AA minimum)
6. THE Live_Tracker_Page SHALL provide text alternatives for all visual information
7. THE Live_Tracker_Page SHALL announce live updates to screen readers using ARIA live regions
8. THE Mode_Badge SHALL have appropriate ARIA role and label
9. THE Team_Radio_Player SHALL provide keyboard controls for audio playback

## Correctness Properties

### CP1: Session Mode Consistency
**Property:** For any given timestamp and session schedule, Session_Mode determination SHALL be deterministic and consistent across all components.

**Test Strategy:** Property-based test that generates random timestamps and session schedules, verifies that Session_API returns consistent mode, and that all components render appropriate UI for that mode.

### CP2: WebSocket Message Ordering
**Property:** When WebSocket messages arrive out of order, the application SHALL display data from the most recent timestamp for each data type.

**Test Strategy:** Property-based test that sends WebSocket messages with random timestamps and verifies that displayed data always reflects the latest timestamp for positions, intervals, and race control.

### CP3: Real-Time Update Performance
**Property:** During live mode, the application SHALL process and render WebSocket updates within 100ms of message receipt, maintaining 60fps.

**Test Strategy:** Performance test that measures time from WebSocket message receipt to DOM update completion, verifying 95th percentile latency is under 100ms.

### CP4: Reconnection Idempotence
**Property:** Multiple reconnection attempts SHALL NOT create duplicate WebSocket connections or duplicate data in the UI.

**Test Strategy:** Property-based test that simulates connection failures and verifies that only one active WebSocket connection exists and no duplicate data appears in panels.

### CP5: Mode Transition Correctness
**Property:** When Session_Mode transitions between live/upcoming/replay, all panels SHALL display data appropriate for the new mode and clean up resources from the previous mode.

**Test Strategy:** Property-based test that simulates mode transitions and verifies WebSocket connections are closed when leaving live mode, polling is stopped when leaving upcoming mode, and all panels render correct data for new mode.

### CP6: Data Synchronization Across Panels
**Property:** All panels displaying the same underlying data (e.g., driver positions) SHALL show consistent information at any given time.

**Test Strategy:** Property-based test that verifies Race_Tower, Gap_Tracker_Chart, and Tyre_Strategy_Panel all display matching driver positions and lap numbers after each update.

### CP7: Responsive Layout Integrity
**Property:** At any viewport width, all panels SHALL be visible and functional without horizontal scrolling or overlapping content.

**Test Strategy:** Visual regression test that captures screenshots at viewport widths 320px, 768px, 1024px, and 1920px, verifying no layout breaks or content overflow.

### CP8: Error Recovery Completeness
**Property:** After any error condition (network failure, API error, invalid data), the application SHALL either recover to a working state or display a clear error message with recovery action.

**Test Strategy:** Fault injection test that simulates various error conditions and verifies application either recovers automatically or provides user-actionable error message.
