# Requirements Document

## Introduction

This document specifies the requirements for migrating the existing Streamlit-based F1 Dashboard to a modern FastAPI backend + React frontend architecture. The migration will transform the monolithic Streamlit application into a scalable, production-ready system with separated concerns, real-time capabilities, and enhanced performance through caching and containerization.

The new architecture will maintain all existing functionality while adding real-time race tracking capabilities, improved data management, and a modern user experience.

## Glossary

- **Backend_API**: The FastAPI server that handles data fetching, processing, and WebSocket connections
- **Frontend_App**: The React + TypeScript application that provides the user interface
- **Service_Layer**: Business logic extracted from Streamlit app for data processing and transformation
- **Jolpica_API**: External API providing historical F1 data from 1950 to present
- **OpenF1_API**: External API providing real-time F1 telemetry data from 2023 onwards
- **WebSocket_Server**: Real-time bidirectional communication channel for live race data
- **Redis_Cache**: In-memory data store for caching API responses with TTL management
- **Docker_Container**: Isolated runtime environment for application components
- **Nginx_Proxy**: Reverse proxy server for routing and load balancing
- **Session_Mode**: Operating mode determining data source (live, upcoming, or replay)
- **Pydantic_Model**: Data validation and serialization schema
- **React_Query**: Data fetching and caching library for React
- **Zustand_Store**: State management solution for React application
- **Analytics_Engine**: Component calculating advanced F1 statistics and metrics
- **Live_Tracker**: Real-time race monitoring interface with telemetry visualization

## Requirements

### Requirement 1: Backend Service Layer Extraction

**User Story:** As a developer, I want to extract the service layer from the Streamlit application, so that business logic can be reused in the FastAPI backend.

#### Acceptance Criteria

1. THE Backend_API SHALL extract all data fetching functions from app.py into a services module
2. THE Backend_API SHALL extract all data transformation functions into a services module
3. THE Backend_API SHALL extract all analytics calculation functions into a services module
4. THE Backend_API SHALL maintain identical function signatures and return types during extraction
5. THE Backend_API SHALL preserve all existing error handling logic
6. THE Backend_API SHALL organize services into logical modules (jolpica_service, analytics_service, openf1_service)

### Requirement 2: FastAPI Application Scaffold

**User Story:** As a developer, I want a properly structured FastAPI application, so that the backend follows best practices and is maintainable.

#### Acceptance Criteria

1. THE Backend_API SHALL implement a modular directory structure with routers, services, models, and config modules
2. THE Backend_API SHALL use Pydantic_Models for all request and response validation
3. THE Backend_API SHALL implement CORS middleware to allow Frontend_App requests
4. THE Backend_API SHALL implement error handling middleware for consistent error responses
5. THE Backend_API SHALL implement health check endpoints for monitoring
6. THE Backend_API SHALL use environment variables for all configuration values
7. THE Backend_API SHALL implement logging with configurable log levels

### Requirement 3: Jolpica API REST Routes

**User Story:** As a frontend developer, I want REST endpoints for historical F1 data, so that I can fetch standings, races, and qualifying results.

#### Acceptance Criteria

1. WHEN a request is made to /api/standings/drivers/{year}, THE Backend_API SHALL return driver standings for the specified year and round
2. WHEN a request is made to /api/standings/constructors/{year}, THE Backend_API SHALL return constructor standings for the specified year and round
3. WHEN a request is made to /api/races/{year}, THE Backend_API SHALL return the race calendar for the specified year
4. WHEN a request is made to /api/races/{year}/{round}/results, THE Backend_API SHALL return race results for the specified year and round
5. WHEN a request is made to /api/races/{year}/{round}/qualifying, THE Backend_API SHALL return qualifying results for the specified year and round
6. WHEN a request is made to /api/races/{year}/{round}/laps, THE Backend_API SHALL return lap times for the specified year and round
7. THE Backend_API SHALL validate all query parameters using Pydantic_Models
8. THE Backend_API SHALL return appropriate HTTP status codes for all error conditions

### Requirement 4: Analytics REST Routes

**User Story:** As a frontend developer, I want REST endpoints for advanced analytics, so that I can display performance trends, consistency scores, and comparative analysis.

#### Acceptance Criteria

1. WHEN a request is made to /api/analytics/trends/{driver_id}/{year}, THE Backend_API SHALL return performance trend data for the specified driver and year
2. WHEN a request is made to /api/analytics/consistency/{driver_id}/{year}, THE Backend_API SHALL return consistency metrics for the specified driver and year
3. WHEN a request is made to /api/analytics/form/{driver_id}/{year}, THE Backend_API SHALL return recent form analysis for the specified driver
4. WHEN a request is made to /api/analytics/dnf/{driver_id}/{year}, THE Backend_API SHALL return DNF statistics for the specified driver and year
5. WHEN a request is made to /api/analytics/compare, THE Backend_API SHALL return comparative metrics for multiple drivers
6. WHEN a request is made to /api/analytics/circuit/{circuit_id}, THE Backend_API SHALL return circuit-specific performance metrics
7. WHEN a request is made to /api/analytics/projection/{year}, THE Backend_API SHALL return championship projection for the specified year
15. THE Analytics_Engine SHALL calculate all metrics using the same algorithms as the Streamlit application

### Requirement 5: OpenF1 API REST Routes

**User Story:** As a frontend developer, I want REST endpoints for real-time F1 data, so that I can display live race information and telemetry.

#### Acceptance Criteria

1. WHEN a request is made to /api/live/session, THE Backend_API SHALL return current session information including session type and status
2. WHEN a request is made to /api/live/drivers, THE Backend_API SHALL return list of drivers in the current session
3. WHEN a request is made to /api/live/positions, THE Backend_API SHALL return current race positions for all drivers
4. WHEN a request is made to /api/live/stints, THE Backend_API SHALL return tire stint information for all drivers
5. WHEN a request is made to /api/live/pits, THE Backend_API SHALL return pit stop data for the current session
6. WHEN a request is made to /api/live/weather, THE Backend_API SHALL return current weather conditions at the circuit
7. WHEN a request is made to /api/live/racecontrol, THE Backend_API SHALL return race control messages and flags
8. WHEN a request is made to /api/live/radio, THE Backend_API SHALL return team radio transcriptions
9. THE Backend_API SHALL determine Session_Mode based on current date and session schedule
10. WHEN Session_Mode is "upcoming", THE Backend_API SHALL return empty data with appropriate status
11. WHEN Session_Mode is "replay", THE Backend_API SHALL return historical session data from OpenF1_API

### Requirement 6: WebSocket Server for Real-Time Updates

**User Story:** As a user, I want real-time race updates without refreshing the page, so that I can follow live races seamlessly.

#### Acceptance Criteria

1. THE WebSocket_Server SHALL accept client connections on /ws/live endpoint
2. WHEN a client connects, THE WebSocket_Server SHALL send initial session state
3. WHILE a live session is active, THE WebSocket_Server SHALL push position updates every 4 seconds
4. WHILE a live session is active, THE WebSocket_Server SHALL push pit stop events immediately when they occur
5. WHILE a live session is active, THE WebSocket_Server SHALL push race control messages immediately when they occur
6. WHILE a live session is active, THE WebSocket_Server SHALL push weather updates every 30 seconds
7. THE WebSocket_Server SHALL handle client disconnections gracefully without affecting other clients
8. THE WebSocket_Server SHALL implement connection heartbeat to detect stale connections
9. WHEN Session_Mode changes from "live" to "completed", THE WebSocket_Server SHALL notify all clients and close connections

### Requirement 7: Redis Caching Layer

**User Story:** As a system administrator, I want API responses cached in Redis, so that the application performs efficiently and reduces external API load.

#### Acceptance Criteria

1. THE Redis_Cache SHALL cache all Jolpica_API responses with a TTL of 3600 seconds
2. THE Redis_Cache SHALL cache analytics calculations with a TTL of 600 seconds
3. THE Backend_API SHALL check Redis_Cache before making external API calls
5. WHEN cached data exists and is not expired, THE Backend_API SHALL return cached data
6. WHEN cached data does not exist or is expired, THE Backend_API SHALL fetch fresh data and update cache
7. THE Backend_API SHALL implement cache key namespacing to prevent collisions
8. THE Backend_API SHALL serialize cache values using JSON format
9. THE Redis_Cache SHALL support cache invalidation by key pattern
10. THE Backend_API SHALL NOT cache live OpenF1_API data as WebSocket_Server handles real-time streaming

### Requirement 8: Pydantic Data Models

**User Story:** As a developer, I want strongly-typed data models, so that data validation and serialization are automatic and reliable.

#### Acceptance Criteria

1. THE Backend_API SHALL define Pydantic_Models for all API request parameters
2. THE Backend_API SHALL define Pydantic_Models for all API response bodies
3. THE Backend_API SHALL define Pydantic_Models for driver standings data structure
4. THE Backend_API SHALL define Pydantic_Models for constructor standings data structure
5. THE Backend_API SHALL define Pydantic_Models for race results data structure
6. THE Backend_API SHALL define Pydantic_Models for qualifying results data structure
7. THE Backend_API SHALL define Pydantic_Models for lap times data structure
8. THE Backend_API SHALL define Pydantic_Models for live session data structure
9. THE Backend_API SHALL define Pydantic_Models for all analytics response types
10. THE Backend_API SHALL validate all incoming requests using Pydantic_Models and return 422 status for validation errors

### Requirement 9: React Application Scaffold

**User Story:** As a frontend developer, I want a modern React application structure, so that the frontend is maintainable and follows best practices.

#### Acceptance Criteria

1. THE Frontend_App SHALL use React 18 with TypeScript for type safety
2. THE Frontend_App SHALL use Vite as the build tool for fast development
3. THE Frontend_App SHALL implement React Router for client-side routing
4. THE Frontend_App SHALL organize components into logical directories (layout, shared, live, analytics)
5. THE Frontend_App SHALL implement a consistent layout component with navigation
6. THE Frontend_App SHALL use Tailwind CSS for component styling
7. THE Frontend_App SHALL implement responsive design for mobile and desktop viewports
8. THE Frontend_App SHALL use environment variables for API endpoint configuration

### Requirement 10: React Query Data Fetching

**User Story:** As a frontend developer, I want declarative data fetching with caching, so that API calls are optimized and state management is simplified.

#### Acceptance Criteria

1. THE Frontend_App SHALL use React_Query for all API data fetching
2. THE Frontend_App SHALL configure React_Query with appropriate stale times and cache times
3. THE Frontend_App SHALL implement custom hooks for each API endpoint
4. THE Frontend_App SHALL handle loading states using React_Query isLoading flag
5. THE Frontend_App SHALL handle error states using React_Query error object
6. THE Frontend_App SHALL implement automatic refetching on window focus for live data
7. THE Frontend_App SHALL implement query invalidation after mutations
8. THE Frontend_App SHALL display loading spinners during data fetching

### Requirement 11: Zustand State Management

**User Story:** As a frontend developer, I want lightweight state management, so that global application state is easy to manage without boilerplate.

#### Acceptance Criteria

1. THE Frontend_App SHALL use Zustand_Store for global application state
2. THE Frontend_App SHALL store selected year in Zustand_Store
3. THE Frontend_App SHALL store selected drivers for comparison in Zustand_Store
4. THE Frontend_App SHALL store live session connection status in Zustand_Store
5. THE Frontend_App SHALL store user preferences (theme, layout) in Zustand_Store
6. THE Frontend_App SHALL persist Zustand_Store state to localStorage
7. THE Frontend_App SHALL provide typed selectors for accessing store state

### Requirement 12: WebSocket Hooks for Real-Time Data

**User Story:** As a frontend developer, I want React hooks for WebSocket connections, so that real-time data integration is simple and reusable.

#### Acceptance Criteria

1. THE Frontend_App SHALL implement a useWebSocket hook for managing WebSocket connections
2. THE useWebSocket hook SHALL automatically connect when component mounts
3. THE useWebSocket hook SHALL automatically disconnect when component unmounts
4. THE useWebSocket hook SHALL implement automatic reconnection with exponential backoff
5. THE useWebSocket hook SHALL parse incoming messages and update local state
6. THE useWebSocket hook SHALL provide connection status (connecting, connected, disconnected, error)
7. THE useWebSocket hook SHALL handle connection errors gracefully
8. THE Frontend_App SHALL implement a useLiveRaceData hook that uses useWebSocket for race updates

### Requirement 13: Page Components Implementation

**User Story:** As a user, I want all existing dashboard pages available in the new React application, so that I have feature parity with the Streamlit version.

#### Acceptance Criteria

1. THE Frontend_App SHALL implement an Overview page displaying next race and latest results
2. THE Frontend_App SHALL implement a Driver Standings page with sortable table and charts
3. THE Frontend_App SHALL implement a Constructor Standings page with sortable table and charts
4. THE Frontend_App SHALL implement a Calendar page displaying the race schedule
5. THE Frontend_App SHALL implement a Races page showing all race results for the selected year
6. THE Frontend_App SHALL implement a Head-to-Head page for driver comparisons
7. THE Frontend_App SHALL implement a Qualifying page showing qualifying results
8. THE Frontend_App SHALL implement a Championship page with progression charts
9. THE Frontend_App SHALL implement a Lap Times page with lap time analysis
10. THE Frontend_App SHALL implement an Analytics page with all 15 analytics endpoints
11. THE Frontend_App SHALL implement a Live Tracker page for real-time race monitoring
12. THE Frontend_App SHALL implement navigation between all pages using React Router

### Requirement 14: Plotly Chart Integration

**User Story:** As a user, I want interactive charts in the React application, so that I can explore data visually like in the Streamlit version.

#### Acceptance Criteria

1. THE Frontend_App SHALL integrate Plotly.js for chart rendering
2. THE Frontend_App SHALL implement horizontal bar charts for standings visualization
3. THE Frontend_App SHALL implement line charts for championship progression
4. THE Frontend_App SHALL implement scatter charts for correlation analysis
5. THE Frontend_App SHALL implement radar charts for multi-dimensional comparisons
6. THE Frontend_App SHALL implement grouped bar charts for comparative analysis
7. THE Frontend_App SHALL apply F1-themed colors to all charts
8. THE Frontend_App SHALL make all charts responsive to viewport size
9. THE Frontend_App SHALL implement chart hover interactions for detailed data display

### Requirement 15: Docker Containerization

**User Story:** As a DevOps engineer, I want the application containerized with Docker, so that deployment is consistent and portable across environments.

#### Acceptance Criteria

1. THE Docker_Container SHALL be created for Backend_API using Python 3.11 base image
2. THE Docker_Container SHALL be created for Frontend_App using Node 20 base image with nginx for serving
3. THE Docker_Container SHALL be created for Redis_Cache using official Redis image
4. THE Docker_Container SHALL be created for Nginx_Proxy using official nginx image
5. THE Backend_API Docker_Container SHALL expose port 8000
6. THE Frontend_App Docker_Container SHALL expose port 80
7. THE Redis_Cache Docker_Container SHALL expose port 6379
8. THE Nginx_Proxy Docker_Container SHALL expose ports 80 and 443
9. THE Docker_Container configuration SHALL use multi-stage builds for optimized image size
10. THE Docker_Container configuration SHALL implement health checks for all services

### Requirement 16: Docker Compose Orchestration

**User Story:** As a developer, I want Docker Compose configuration, so that I can run the entire application stack with a single command.

#### Acceptance Criteria

1. THE Docker Compose configuration SHALL define all four services (api, web, redis, nginx)
2. THE Docker Compose configuration SHALL create a shared network for service communication
3. THE Docker Compose configuration SHALL define volume mounts for Redis data persistence
4. THE Docker Compose configuration SHALL define environment variables for each service
5. THE Docker Compose configuration SHALL implement service dependencies (api depends on redis)
6. THE Docker Compose configuration SHALL implement restart policies for all services
7. THE Docker Compose configuration SHALL expose only nginx ports to the host
8. THE Docker Compose configuration SHALL support development and production profiles

### Requirement 17: Nginx Reverse Proxy Configuration

**User Story:** As a system administrator, I want Nginx as a reverse proxy, so that API and frontend requests are properly routed and the application is production-ready.

#### Acceptance Criteria

1. THE Nginx_Proxy SHALL route requests to /api/* to Backend_API on port 8000
2. THE Nginx_Proxy SHALL route requests to /ws/* to Backend_API WebSocket endpoint
3. THE Nginx_Proxy SHALL route all other requests to Frontend_App on port 80
4. THE Nginx_Proxy SHALL implement gzip compression for text responses
5. THE Nginx_Proxy SHALL implement caching headers for static assets
6. THE Nginx_Proxy SHALL implement rate limiting for API endpoints
7. THE Nginx_Proxy SHALL implement request size limits
8. THE Nginx_Proxy SHALL log all requests with timestamps and status codes
9. THE Nginx_Proxy SHALL support WebSocket upgrade headers for /ws/* routes

### Requirement 18: Environment Configuration Management

**User Story:** As a developer, I want environment-based configuration, so that the application can run in different environments without code changes.

#### Acceptance Criteria

1. THE Backend_API SHALL read all configuration from environment variables
2. THE Backend_API SHALL provide default values for all optional configuration
3. THE Backend_API SHALL validate required environment variables on startup
4. THE Frontend_App SHALL read API endpoint URL from environment variables
5. THE Frontend_App SHALL support .env files for local development
6. THE Docker Compose configuration SHALL load environment variables from .env file
7. THE application SHALL document all required and optional environment variables
8. THE application SHALL fail fast with clear error messages for missing required configuration

### Requirement 19: Backend Testing Infrastructure

**User Story:** As a developer, I want comprehensive backend tests, so that I can verify correctness and catch regressions.

#### Acceptance Criteria

1. THE Backend_API SHALL use pytest as the testing framework
2. THE Backend_API SHALL use Hypothesis for property-based testing
3. THE Backend_API SHALL implement unit tests for all service layer functions
4. THE Backend_API SHALL implement integration tests for all API endpoints
5. THE Backend_API SHALL implement property-based tests for data transformation functions
6. THE Backend_API SHALL implement tests for cache behavior
7. THE Backend_API SHALL implement tests for WebSocket connections
8. THE Backend_API SHALL achieve minimum 80% code coverage
9. THE Backend_API SHALL implement test fixtures for common test data
10. THE Backend_API SHALL mock external API calls in tests

### Requirement 20: Frontend Testing Infrastructure

**User Story:** As a developer, I want comprehensive frontend tests, so that I can verify UI behavior and catch regressions.

#### Acceptance Criteria

1. THE Frontend_App SHALL use Vitest as the testing framework
2. THE Frontend_App SHALL use React Testing Library for component tests
3. THE Frontend_App SHALL implement unit tests for all custom hooks
4. THE Frontend_App SHALL implement component tests for all page components
5. THE Frontend_App SHALL implement tests for user interactions (clicks, form submissions)
6. THE Frontend_App SHALL implement tests for data fetching and loading states
7. THE Frontend_App SHALL implement tests for error handling
8. THE Frontend_App SHALL mock API calls using MSW (Mock Service Worker)
9. THE Frontend_App SHALL achieve minimum 70% code coverage

### Requirement 21: Session Mode Logic

**User Story:** As a user, I want the application to automatically determine if a race is live, upcoming, or completed, so that I see the most relevant data source.

#### Acceptance Criteria

1. THE Backend_API SHALL determine Session_Mode by comparing current time with session schedule
2. WHEN current time is before session start, THE Backend_API SHALL set Session_Mode to "upcoming"
3. WHEN current time is during session window, THE Backend_API SHALL set Session_Mode to "live"
4. WHEN current time is after session end, THE Backend_API SHALL set Session_Mode to "replay"
5. WHEN Session_Mode is "live", THE Backend_API SHALL fetch data from OpenF1_API
6. WHEN Session_Mode is "replay", THE Backend_API SHALL fetch historical data from OpenF1_API
7. WHEN Session_Mode is "upcoming", THE Backend_API SHALL return next session information
8. THE Backend_API SHALL expose Session_Mode in /api/live/session endpoint
9. THE Frontend_App SHALL display Session_Mode indicator in Live Tracker page

### Requirement 22: Data Migration and Validation

**User Story:** As a developer, I want to validate that migrated functionality produces identical results, so that I can ensure correctness during migration.

#### Acceptance Criteria

1. THE Backend_API SHALL produce identical driver standings output as Streamlit app for the same input
2. THE Backend_API SHALL produce identical constructor standings output as Streamlit app for the same input
3. THE Analytics_Engine SHALL produce identical analytics calculations as Streamlit app for the same input
4. THE Backend_API SHALL handle all edge cases that Streamlit app handles (null values, missing data, DNFs)
5. THE Backend_API SHALL apply the same sorting and filtering logic as Streamlit app
6. THE Backend_API SHALL format dates and times consistently with Streamlit app
7. THE Backend_API SHALL round numerical values consistently with Streamlit app

### Requirement 23: API Documentation

**User Story:** As a frontend developer, I want comprehensive API documentation, so that I can understand and use all backend endpoints.

#### Acceptance Criteria

1. THE Backend_API SHALL generate OpenAPI documentation automatically using FastAPI
2. THE Backend_API SHALL serve interactive API documentation at /docs endpoint
3. THE Backend_API SHALL serve alternative API documentation at /redoc endpoint
4. THE Backend_API SHALL document all request parameters with types and descriptions
5. THE Backend_API SHALL document all response schemas with examples
6. THE Backend_API SHALL document all possible error responses
7. THE Backend_API SHALL document authentication requirements (if any)
8. THE Backend_API SHALL document rate limits and caching behavior

### Requirement 24: Error Handling and Logging

**User Story:** As a system administrator, I want comprehensive error handling and logging, so that I can diagnose issues and monitor application health.

#### Acceptance Criteria

1. THE Backend_API SHALL log all incoming requests with method, path, and timestamp
2. THE Backend_API SHALL log all external API calls with URL and response time
3. THE Backend_API SHALL log all errors with stack traces and context
4. THE Backend_API SHALL return consistent error response format for all errors
5. THE Backend_API SHALL return appropriate HTTP status codes for different error types
6. THE Backend_API SHALL implement request ID tracking for distributed tracing
7. THE Frontend_App SHALL display user-friendly error messages for all error conditions
8. THE Frontend_App SHALL log errors to console in development mode
9. THE Frontend_App SHALL implement error boundaries to prevent full application crashes

### Requirement 25: Performance Optimization

**User Story:** As a user, I want fast page loads and smooth interactions, so that the application feels responsive and professional.

#### Acceptance Criteria

1. THE Frontend_App SHALL implement code splitting for route-based lazy loading
2. THE Frontend_App SHALL implement virtual scrolling for large data tables
3. THE Frontend_App SHALL debounce user input for search and filter operations
4. THE Frontend_App SHALL optimize chart rendering for large datasets
5. THE Backend_API SHALL implement database query optimization (if applicable)
6. THE Backend_API SHALL implement response compression for large payloads
7. THE Backend_API SHALL implement connection pooling for external API calls
8. THE Redis_Cache SHALL reduce external API calls by at least 80% under normal load
9. THE Frontend_App SHALL achieve Lighthouse performance score above 90

### Requirement 26: Jolpica API Parser

**User Story:** As a developer, I want a robust parser for Jolpica API responses, so that historical F1 data is correctly transformed into application models.

#### Acceptance Criteria

1. THE Backend_API SHALL parse Jolpica_API JSON responses into Pydantic_Models
2. THE Backend_API SHALL handle missing fields in Jolpica_API responses with default values
3. THE Backend_API SHALL validate data types during parsing
4. WHEN Jolpica_API returns invalid data, THE Backend_API SHALL log the error and return appropriate error response
5. THE Backend_API SHALL implement a pretty printer for Pydantic_Models to JSON
6. FOR ALL valid Pydantic_Models, parsing then printing then parsing SHALL produce an equivalent object (round-trip property)

### Requirement 27: OpenF1 API Parser

**User Story:** As a developer, I want a robust parser for OpenF1 API responses, so that real-time F1 data is correctly transformed into application models.

#### Acceptance Criteria

1. THE Backend_API SHALL parse OpenF1_API JSON responses into Pydantic_Models
2. THE Backend_API SHALL handle missing fields in OpenF1_API responses with default values
3. THE Backend_API SHALL validate data types during parsing
4. WHEN OpenF1_API returns invalid data, THE Backend_API SHALL log the error and return appropriate error response
5. THE Backend_API SHALL implement a pretty printer for Pydantic_Models to JSON
6. FOR ALL valid Pydantic_Models, parsing then printing then parsing SHALL produce an equivalent object (round-trip property)

### Requirement 28: Migration Phase Execution

**User Story:** As a project manager, I want the migration executed in phases, so that progress is trackable and risks are minimized.

#### Acceptance Criteria

1. THE migration SHALL be executed in 12 sequential phases
2. Phase 1 SHALL extract service layer from Streamlit app
3. Phase 2 SHALL create FastAPI scaffold with basic structure
4. Phase 3 SHALL implement Jolpica REST routes
5. Phase 4 SHALL implement Analytics REST routes
6. Phase 5 SHALL implement OpenF1 REST routes
7. Phase 6 SHALL implement WebSocket server
8. Phase 7 SHALL create React scaffold with routing
9. Phase 8 SHALL implement historical data pages (Overview through Lap Times)
10. Phase 9 SHALL implement Advanced Analytics page
11. Phase 10 SHALL implement Live Race Tracker page
12. Phase 11 SHALL implement Docker containerization and Nginx configuration
13. Phase 12 SHALL implement testing infrastructure and final polish
14. WHEN each phase completes, THE migration SHALL be validated before proceeding to next phase

## Correctness Properties

### CP1: API Response Consistency
**Property:** For identical input parameters, the FastAPI backend SHALL return identical data as the Streamlit application for all historical data endpoints.

**Test Strategy:** Property-based test that generates random valid year/round combinations and verifies FastAPI responses match Streamlit app output for driver standings, constructor standings, race results, and analytics calculations.

### CP2: Round-Trip Serialization
**Property:** For all Pydantic models, serializing to JSON then deserializing SHALL produce an equivalent object.

**Test Strategy:** Property-based test using Hypothesis to generate random valid model instances, serialize to JSON, deserialize back, and verify equality. This ensures parsers and serializers are correct inverses.

### CP3: Cache Consistency
**Property:** Cached data SHALL be identical to fresh API data within the TTL window, and cache invalidation SHALL always fetch fresh data.

**Test Strategy:** Property-based test that verifies cached responses match fresh API responses, and that cache expiration correctly triggers new API calls.

### CP4: WebSocket Message Ordering
**Property:** WebSocket messages SHALL be delivered to clients in the same order they are sent by the server.

**Test Strategy:** Property-based test that sends sequences of messages and verifies clients receive them in identical order.

### CP5: Session Mode Determination
**Property:** Session mode SHALL be deterministic based on current time and session schedule, and SHALL transition correctly between modes.

**Test Strategy:** Property-based test that generates various time/schedule combinations and verifies correct mode determination and transitions.

### CP6: Analytics Calculation Invariants
**Property:** Analytics calculations SHALL maintain mathematical invariants (e.g., consistency score between 0-100, DNF rate between 0-1, percentile rankings sum to expected distribution).

**Test Strategy:** Property-based test that verifies all analytics outputs satisfy their mathematical constraints regardless of input data.

### CP7: Sorting Preservation
**Property:** Driver and constructor standings SHALL always be sorted by points descending, with ties broken by wins, matching F1 championship rules.

**Test Strategy:** Property-based test that generates various standings scenarios and verifies sorting order matches F1 rules exactly.

### CP8: Error Handling Completeness
**Property:** All API endpoints SHALL handle all error conditions (network errors, invalid input, missing data, external API failures) without crashing and SHALL return appropriate HTTP status codes.

**Test Strategy:** Property-based test that simulates various failure modes and verifies graceful error handling with correct status codes.

### CP9: Data Transformation Idempotence
**Property:** Applying data transformation functions multiple times SHALL produce the same result as applying once (idempotence).

**Test Strategy:** Property-based test that verifies f(x) = f(f(x)) for all data transformation functions.

### CP10: React Component Rendering Stability
**Property:** React components SHALL render consistently for the same props and state, without unnecessary re-renders.

**Test Strategy:** Property-based test using React Testing Library to verify component output stability and render count optimization.
