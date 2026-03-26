**F1 DASHBOARD**

**FastAPI + React**

Architecture & Implementation Specification

**FastAPI · React · WebSockets · Redis · Jolpica · OpenF1**

Version 2.0 · March 2026

**1. Overview**

This document specifies the full architecture for the F1 Dashboard rebuilt on FastAPI (Python backend) and React (TypeScript frontend). It supersedes the Streamlit-based specification.

The primary motivation for this stack is the Live Race Tracker, which requires true WebSocket push for OpenF1 interval data (4-second updates), car telemetry at 3.7 Hz, and instant race control event delivery --- none of which are achievable in Streamlit. Every other tab benefits through improved mobile responsiveness, concurrent user support, and a proper typed API layer.

  ---------------------------- ------------------------------------ ---------------------------------------------
  **Concern**                  **Streamlit (before)**               **FastAPI + React (new)**

  **Real-time data**           30--60s polling via st.fragment      True WebSocket push, 4s latency

  **Concurrent users**         Degrades after ~10 users            Handles 100s via async Python

  **UI customisation**         Limited to Streamlit widgets         Full React --- any component, any layout

  **Mobile experience**        Not responsive                       Fully responsive with Tailwind CSS

  **Car telemetry (3.7 Hz)**   Impossible                           Native via WebSocket streaming

  **Deployment**               streamlit run app.py                 Docker Compose: API + frontend + Redis

  **Caching**                  @st.cache_data (in-process)         Redis (shared across all workers)

  **State management**         st.session_state (per browser tab)   React Query + Zustand (proper client state)

  **Testing**                  pytest only                          pytest (backend) + Vitest (frontend)

  **API documentation**        None                                 Auto-generated Swagger UI at /docs

  **Language**                 Python only                          Python backend + TypeScript frontend
  ---------------------------- ------------------------------------ ---------------------------------------------

**2. High-Level Architecture**

**2.1 System topology**

Four Docker containers run behind an Nginx reverse proxy:

-   api --- FastAPI served by Uvicorn; REST + WebSocket endpoints on port 8000

-   web --- React + Vite build served by Nginx; port 3000 in dev, 80 in production

-   redis --- Redis 7 on port 6379; shared cache across all API workers

-   nginx --- single entry point on port 80; routes traffic to the correct container

**2.2 REST request flow**

1.  Browser sends GET /api/standings/drivers/2025

2.  Nginx routes /api/* to FastAPI container on port 8000

3.  Router calls service function fetch_driver_standings('2025')

4.  Service checks Redis for key standings:drivers:2025

5.  Cache miss: calls Jolpica API, parses response, writes to Redis with 1h TTL

6.  Cache hit: returns result directly without hitting Jolpica

7.  Router serialises result through Pydantic model and returns JSON 200

**2.3 WebSocket flow --- Live Race Tracker**

8.  Browser opens ws://nginx/ws/live/{session_key}

9.  Nginx upgrades connection and proxies to FastAPI WebSocket handler

10. ConnectionManager registers client in active_connections[session_key]

11. Background asyncio task starts polling OpenF1 every 4 seconds

12. Each cycle assembles positions + intervals + race_control into one JSON payload

13. Payload broadcast to all clients watching the same session_key

14. React receives message; Zustand liveRaceStore updates; only affected components re-render

15. On last client disconnect, background task stops to avoid unnecessary polling

**3. Directory Structure**

  ------------------------------------------------ --------------------------------------------------------------------------------
  **Path**                                         **Responsibility**

  **backend/app/main.py**                          FastAPI app entry point; mounts all routers; configures CORS; WebSocket routes

  **backend/app/routers/standings.py**             Driver + constructor standings endpoints

  **backend/app/routers/races.py**                 Race results, qualifying, lap times endpoints

  **backend/app/routers/analytics.py**             All 15 analytics calculation endpoints

  **backend/app/routers/live.py**                  OpenF1 live session REST endpoints

  **backend/app/routers/ws.py**                    WebSocket route registration

  **backend/app/services/jolpica.py**              All fetch_* and parse_* functions ported from Streamlit

  **backend/app/services/openf1.py**               All OpenF1 fetch functions; session resolver; driver registry

  **backend/app/services/analytics.py**            All calculate_analytics_* functions; unchanged from Streamlit

  **backend/app/services/live.py**                 Session state manager; tyre colour mapping; form helpers... **backend/app/cache/redis.py**                   Async Redis client; @redis_cache decorator; invalidation helpers

  **backend/app/models/**                          Pydantic v2 response models for every endpoint

  **backend/app/ws/manager.py**                    ConnectionManager; per-session broadcast; background poll tasks

  **backend/tests/test_analytics.py**              Unit tests for analytics service functions

  **backend/tests/test_analytics_properties.py**   Hypothesis property-based tests (26 properties)

  **backend/tests/test_routes.py**                 FastAPI route integration tests via httpx.AsyncClient

  **frontend/src/pages/**                          One .tsx file per dashboard tab

  **frontend/src/components/**                     Reusable components: RaceTower, TyreStrategy, GapChart, etc.

  **frontend/src/hooks/**                          Custom hooks: useLiveRace, useWebSocket, useAnalytics, useStandings

  **frontend/src/api/**                            Axios client; typed request/response functions per endpoint group

  **frontend/src/store/**                          Zustand stores: liveRaceStore, sessionStore, userPrefsStore

  **frontend/src/types/**                          TypeScript interfaces mirroring Pydantic models

  **docker-compose.yml**                           Orchestrates: api, web, redis, nginx containers

  **nginx/nginx.conf**                             Routes /api/* and /ws/* to FastAPI; /* to React

  **.env / .env.frontend**                         Environment variables for both services (see section 9)
  ------------------------------------------------ --------------------------------------------------------------------------------

**4. Backend --- FastAPI**

**4.1 Application entry point**

main.py creates the FastAPI instance, registers all routers, configures CORS, and handles Redis pool lifecycle via FastAPI lifespan events:

> app = FastAPI(title='F1 Dashboard API', version='2.0', lifespan=lifespan)

> app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, ...)

> app.include_router(standings_router, prefix='/api')

> app.include_router(races_router, prefix='/api')

> app.include_router(analytics_router, prefix='/api')

> app.include_router(live_router, prefix='/api')

> app.include_router(ws_router) # WebSocket routes --- no /api prefix

**4.2 Service layer --- ported Python logic**

The service layer is a direct migration of app.py's pure functions. Because the Streamlit version was designed with calculation functions free of st.* imports, the migration is mostly copy-paste with three changes:

-   Replace @st.cache_data with @redis_cache(ttl=N) --- a custom async decorator described below

-   Replace st.warning() / st.error() inside calculation functions with returned None or raised exceptions --- routers handle error surfacing

-   Replace requests with httpx.AsyncClient --- required for non-blocking calls inside FastAPI's async event loop

**services/analytics.py**

All 15 calculate_analytics_* functions are copied from app.py unchanged. Each is wrapped with @redis_cache(ttl=3600). The function signatures, algorithms, and return structures are identical to the Streamlit version --- all 26 Hypothesis property tests continue to pass without modification.

**services/jolpica.py**

All fetch_* and parse_* functions use a shared httpx.AsyncClient with connection pooling. The base URL and retry logic are configured from environment variables.

**services/openf1.py**

OpenF1 fetch functions plus a session_resolver() function that calls /sessions?session_key=latest, compares current UTC time against date_start/date_end, and returns mode ('live', 'upcoming', or 'replay') alongside the resolved integer session_key.

**4.3 Redis cache decorator**

> def redis_cache(ttl: int = 3600):

> def decorator(func):

> @wraps(func)

> async def wrapper(*args, **kwargs):

> key = f'{func.__name__}:{hash(str(args)+str(sorted(kwargs.items())))}'

> cached = await redis_client.get(key)

> if cached:

> return json.loads(cached)

> result = await func(*args, **kwargs)

> await redis_client.setex(key, ttl, json.dumps(result, default=str))

> return result

> return wrapper

> return decorator

**4.4 Pydantic response models (key examples)**

-   DriverStanding --- position, points, wins, driver: DriverInfo, constructor: ConstructorInfo

-   ConsistencyResponse --- consistency_score: float, std_dev: float, avg_position: float, completed_races: int, total_races: int

-   FormResponse --- avg_position: float, total_points: int, trend_direction: Literal['improving','declining','stable'], trend_slope: float, races_analyzed: int

-   LiveSession --- session_key: int, meeting_key: int, session_type: str, mode: Literal['live','upcoming','replay'], date_start: datetime, circuit_short_name: str

-   Stint --- driver_number: int, compound: str, lap_start: int, lap_end: int, tyre_age_at_start: int

-   RaceControlEvent --- category: str, flag: str | None, message: str, lap_number: int | None, scope: str, date: datetime

**4.5 REST API endpoints**

  ------------ ----------------------------------------------- --------------- --------------------------------- -----------------------------------------------
  **Method**   **Endpoint**                                    **Router**      **Response**                      **Description**

  **GET**      /api/standings/drivers/{year}                   standings.py    200 list[DriverStanding]        Driver championship table for a season

  **GET**      /api/standings/constructors/{year}              standings.py    200 list[ConstructorStanding]   Constructor championship table

  **GET**      /api/races/{year}                               races.py        200 list[Race]                  All races and results for a season

  **GET**      /api/races/{year}/{round}                       races.py        200 RaceDetail                    Single race full result with driver details

  **GET**      /api/qualifying/{year}/{round}                  races.py        200 list[QualifyingResult]      Q1/Q2/Q3 times and grid positions

  **GET**      /api/laps/{year}/{round}                        races.py        200 list[LapTime]               Fastest laps per driver for a race

  **GET**      /api/drivers/{driver_id}/results/{year}         races.py        200 list[DriverRaceResult]      Season results for one driver

  **GET**      /api/analytics/trends/{driver_id}/{year}        analytics.py    200 TrendsResponse                Position/points trend over season

  **GET**      /api/analytics/consistency/{driver_id}/{year}   analytics.py    200 ConsistencyResponse           Consistency score, std dev, avg position

  **GET**      /api/analytics/form/{driver_id}/{year}          analytics.py    200 FormResponse                  Recent form: trend direction + slope

  **GET**      /api/analytics/dnf/{driver_id}/{year}           analytics.py    200 DNFResponse                   DNF rate and cause breakdown

  **GET**      /api/analytics/compare                          analytics.py    200 CompareResponse               Multi-driver comparison (query params)

  **GET**      /api/analytics/circuit/{circuit_id}             analytics.py    200 CircuitResponse               Circuit difficulty + historical performance

  **GET**      /api/analytics/projection/{year}                analytics.py    200 ProjectionResponse            Championship projection: 3 scenarios

  **GET**      /api/live/session                               live.py         200 LiveSession                   Current session + mode (live/upcoming/replay)

  **GET**      /api/live/drivers/{session_key}                 live.py         200 list[Driver]                Driver registry for a session

  **GET**      /api/live/positions/{session_key}               live.py         200 list[Position]              Current race positions

  **GET**      /api/live/stints/{session_key}                  live.py         200 list[Stint]                 All stints with compound and tyre age

  **GET**      /api/live/pits/{session_key}                    live.py         200 list[PitStop]               All pit stops with stop duration

  **GET**      /api/live/weather/{session_key}                 live.py         200 list[Weather]               Weather readings for the session

  **GET**      /api/live/racecontrol/{session_key}             live.py         200 list[RaceControlEvent]      All race control messages and flags

  **GET**      /api/live/radio/{session_key}                   live.py         200 list[TeamRadio]             Team radio clips with audio URLs

  **WS**       /ws/live/{session_key}                          ws/manager.py   JSON stream                       Positions + intervals + race control at ~4s

  **WS**       /ws/telemetry/{session_key}/{driver}            ws/manager.py   JSON stream                       Car data: speed, throttle, brake at 3.7 Hz
  ------------ ----------------------------------------------- --------------- --------------------------------- -----------------------------------------------

**4.6 WebSocket endpoints**

  --------------------------------------------- ------------------------------------------------------------ -------------------------------------------------------------------
  **Channel**                                   **Payload fields**                                           **Behaviour**

  /ws/live/{session_key}                        positions, intervals, race_control, weather                  Broadcast to all clients on same session; fires every ~4s

  /ws/telemetry/{session_key}/{driver_number}   speed, throttle, brake, rpm, drs, gear, x, y, z              Per-driver stream at ~3.7 Hz; starts only when client subscribes

  /ws/timing/{session_key}                      lap_number, sector_1, sector_2, sector_3, is_personal_best   Event-driven; fires when each sector is completed
  --------------------------------------------- ------------------------------------------------------------ -------------------------------------------------------------------

**ConnectionManager**

Maintains a dict of active_connections keyed by session_key. A per-session background asyncio task is created on first connect and cancelled when the last client disconnects, preventing unnecessary OpenF1 polling between race sessions.

> class ConnectionManager:

> def __init__(self):

> self.connections: dict[str, list[WebSocket]] = {}

> self.tasks: dict[str, asyncio.Task] = {}

> async def connect(self, ws: WebSocket, session_key: str):

> await ws.accept()

> self.connections.setdefault(session_key, []).append(ws)

> if session_key not in self.tasks:

> self.tasks[session_key] = asyncio.create_task(

> self._poll_loop(session_key))

> async def broadcast(self, session_key: str, data: dict):

> for ws in self.connections.get(session_key, []):

> await ws.send_json(data)

**5. Frontend --- React + TypeScript**

**5.1 Pages**

  ----------------------- ------------------------- ------------------------------ ---------------------------------------------------------------
  **Page**                **Route**                 **Component**                  **Key content**

  Home / Overview         /                         OverviewPage.tsx               Season summary cards, latest race winner, championship leader

  Driver Standings        /standings/drivers        DriverStandingsPage.tsx        Points table + interactive Plotly bar chart

  Constructor Standings   /standings/constructors   ConstructorStandingsPage.tsx   Team points + stacked bar chart by driver

  Race Calendar           /calendar                 CalendarPage.tsx               Season schedule table + countdown to next race

  All Races               /races                    RacesPage.tsx                  Dropdown race selector + full result table

  Head to Head            /h2h                      HeadToHeadPage.tsx             Two-driver comparison with metric cards

  Qualifying              /qualifying               QualifyingPage.tsx             Grid positions, Q1/Q2/Q3 times, gap to pole

  Championship Battle     /championship             ChampionshipPage.tsx           Cumulative points progression line chart

  Lap Times               /laps                     LapTimesPage.tsx               Fastest laps and sector breakdowns per race

  Advanced Analytics      /analytics                AnalyticsPage.tsx              5 sub-sections with radar, scatter, trend charts

  **Live Race Tracker**   /live                     LiveTrackerPage.tsx            7 real-time panels; WebSocket; auto-detects mode
  ----------------------- ------------------------- ------------------------------ ---------------------------------------------------------------

**5.2 Components**

  ------------------- --------------------------------- ------------------------------------------------------------------
  **Component**       **Used in**                       **What it renders**

  RaceTower           LiveTrackerPage                   Live P1--P20 leaderboard from WS; overtake badges; gap to leader

  GapChart            LiveTrackerPage                   Gap-to-leader line chart over laps; recharts or Plotly

  TyreStrategy        LiveTrackerPage + AnalyticsPage   Stint bars per driver; compound colour-coded; tyre age tooltip

  PitStopList         LiveTrackerPage                   Stop duration ranking; fastest stop badge; cumulative time lost

  WeatherPanel        LiveTrackerPage                   Track/air temp gauges; rainfall indicator; wind direction arrow

  RaceControlFeed     LiveTrackerPage                   Scrollable append-only event log; colour-coded by event type

  TeamRadioPlayer     LiveTrackerPage                   Audio player per driver; timestamp; team colour header

  TelemetryChart      LiveTrackerPage (optional)        Speed/throttle/brake over time at 3.7 Hz; driver selector

  ConsistencyGauge    AnalyticsPage                     0--100 arc gauge for consistency score

  FormIndicator       AnalyticsPage                     Trend arrow up/down/flat with slope and last-N avg position

  RadarChart          AnalyticsPage (Comparative)       Multi-driver radar via Plotly scatterpolar

  SessionModeBadge    LiveTrackerPage                   LIVE / UPCOMING / REPLAY pill; colour changes with mode

  DriverSelector      Shared                            Searchable dropdown; team colour swatch; driver number

  SeasonSelector      Shared                            Year dropdown; defaults to current; range mode for analytics
  DriverCard          Standings + Analytics             Headshot from OpenF1 headshot_url; name; team; number
  ------------------- --------------------------------- ------------------------------------------------------------------

**5.3 State management**

  ---------------------------- ----------------- -----------------------------------------------------------------------
  **Tool**                     **State type**    **What it manages**

  React Query                  Server state      All REST API calls; caching; background refresh; loading/error states

  Zustand --- liveRaceStore    WebSocket state   Positions, intervals, race control events from WS stream

  Zustand --- sessionStore     Session state     Active session_key, meeting_key, mode (live/upcoming/replay)

  Zustand --- userPrefsStore   UI preferences    Selected year, favourite drivers, preferred colour scheme

  React Router                 Navigation        Client-side routing; URL reflects current page and params

  URL search params            Shareable state   Driver IDs, season, metric type encoded in URL for sharing
  ---------------------------- ----------------- -----------------------------------------------------------------------

**5.4 Custom WebSocket hook**

> const useWebSocket = (sessionKey: string) => {

> const setPositions = useLiveRaceStore(s => s.setPositions)

> const setIntervals = useLiveRaceStore(s => s.setIntervals)

> const appendRCEvent = useLiveRaceStore(s => s.appendRaceControlEvent)

> useEffect(() => {

> if (!sessionKey) return

> const ws = new WebSocket(`${import.meta.env.VITE_WS_BASE_URL}/ws/live/${sessionKey}`)

> ws.onmessage = (e) => {

> const { positions, intervals, race_control } = JSON.parse(e.data)

> setPositions(positions)

> setIntervals(intervals)

> race_control.forEach(appendRCEvent)

> }

> ws.onclose = () => console.log('WS closed for session', sessionKey)

> return () => ws.close()

> }, [sessionKey])

> }

**5.5 Plotly chart migration**

The backend's create_analytics_* functions return Plotly figure configs as dicts. The API serialises them as JSON. React renders them via react-plotly.js without any chart logic being rewritten in TypeScript:

> // GET /api/analytics/trends/verstappen/2025 returns:

> // { data: [{type:'scatter', x:[...], y:[...]}], layout: {title:...} }

> // React component:

> <Plot

> data={figure.data}

> layout={{ ...figure.layout, autosize: true }}

> useResizeHandler

> style={{ width: '100%' }}

> />

**6. Live Race Tracker --- Real-Time Detail**

**6.1 Session modes**

-   live --- active race session; WebSocket opened immediately; all 7 panels receive streaming data

-   upcoming --- next session is in the future; circuit info, starting grid, countdown timer displayed

-   replay --- no active session; user selects any past session_key; all panels load from REST endpoints with cached historical data

**6.2 Panel data sources in live mode**

-   RaceTower + GapChart --- Zustand liveRaceStore (WebSocket broadcast, ~4s update)

-   RaceControlFeed --- Zustand liveRaceStore (WebSocket, append-only)

-   TyreStrategy --- React Query staleTime: 90s (re-fetches when lap count increases)

-   PitStopList --- React Query staleTime: 60s

-   WeatherPanel --- React Query staleTime: 120s

-   TeamRadioPlayer --- React Query staleTime: 300s

**6.3 Tyre compound colour constants**

> export const TYRE_COLORS: Record<string, string> = {

> SOFT: '#E8002D', // red

> MEDIUM: '#FFF200', // yellow

> HARD: '#CCCCCC', // light gray (dark border applied by component)

> INTERMEDIATE: '#39B54A', // green

> WET: '#0067FF', // blue

> }

**7. Caching Strategy**

  -------------------------------- ------------------ --------------- -------------------------------------------------------
  **Data**                         **TTL**            **Source**      **Strategy**

  Driver / constructor standings   1 hour             Jolpica         Invalidate when new race round completes

  Race results (completed round)   24 hours           Jolpica         Effectively permanent once race finishes

  Analytics calculations           1 hour             Service layer   Key = function_name + driver_id + year + metric

  Live session info                30 seconds         OpenF1          Short TTL; session state can flip to 'live' quickly

  Driver registry for session      Session duration   OpenF1          Rebuild only on session_key change
  Live positions / intervals       **Not cached**     OpenF1 WS       WebSocket stream bypasses Redis entirely

  Stints for a session             90 seconds         OpenF1          Re-fetch when lap count increases

  Pit stop data                    60 seconds         OpenF1          Append-only; new stops added on each poll

  Weather readings                 2 minutes          OpenF1          Keep last N readings for history chart

  Race control events              60 seconds         OpenF1          Diff against last_seen_date; append new only

  Team radio URLs                  5 minutes          OpenF1          Permanent once published; aggressive cache fine

  Car telemetry / location         **Not cached**     OpenF1 WS       Raw stream direct to WebSocket client
  -------------------------------- ------------------ --------------- -------------------------------------------------------

**8. Testing Strategy**

  ----------------------- --------------------- -------------------------------------------------------------------------------
  **Tool**                **Layer**             **What it covers**

  pytest                  Backend unit          Service functions; analytics calculations; Jolpica + OpenF1 with mocked httpx

  pytest-asyncio          Backend async         FastAPI route handlers; async Redis; WebSocket lifecycle

  httpx AsyncClient       Backend integration   Full request/response cycle for every REST endpoint

  hypothesis              Backend property      26 analytics correctness properties; 100+ random inputs each

  Vitest                  Frontend unit         Custom hooks; utility functions; Zustand store actions

  React Testing Library   Frontend component    RaceTower render; TyreStrategy colours; SessionModeBadge state

  Playwright (future)     E2E                   Full browser tests: navigate Live Tracker; verify WS data appears
  ----------------------- --------------------- -------------------------------------------------------------------------------

**Running tests**

> # Backend --- all tests with coverage

> cd backend && pytest tests/ --cov=app --cov-report=html

> # Backend --- property tests only

> pytest tests/test_analytics_properties.py -v

> # Frontend

> cd frontend && npx vitest run --coverage

**9. Environment Variables**

  ----------------------- --------------- -------------------------------------------------------------------
  **Variable**            **Required?**   **Value / notes**

  **JOLPICA_BASE_URL**    **Required**    https://api.jolpi.ca/ergast/f1

  **OPENF1_BASE_URL**     **Required**    https://api.openf1.org/v1

  **OPENF1_API_KEY**      Optional        Paid key for live real-time data; omit for historical replay only

  **REDIS_URL**           **Required**    redis://localhost:6379/0

  **REDIS_TTL_SHORT**     Optional        Default 30 --- seconds for live session data

  **REDIS_TTL_LONG**      Optional        Default 3600 --- seconds for standings + analytics

  **CORS_ORIGINS**        **Required**    http://localhost:3000 in dev; production URL in prod

  **WS_PING_INTERVAL**    Optional        Default 20 --- WebSocket keep-alive ping in seconds

  **LOG_LEVEL**           Optional        INFO in prod, DEBUG in dev

  **VITE_API_BASE_URL**   Frontend        http://localhost:8000 in dev; production API URL in prod

  **VITE_WS_BASE_URL**    Frontend        ws://localhost:8000 in dev; wss://your-domain in prod
  ----------------------- --------------- -------------------------------------------------------------------

**10. Docker and Deployment**

**10.1 docker-compose.yml structure**

> services:

> api:

> build: ./backend

> ports: ['8000:8000']

> env_file: .env

> depends_on: [redis]

> web:

> build: ./frontend

> ports: ['3000:80']

> env_file: .env.frontend

> redis:

> image: redis:7-alpine

> ports: ['6379:6379']

> nginx:

> image: nginx:1.25-alpine

> ports: ['80:80']

> volumes: ['./nginx/nginx.conf:/etc/nginx/nginx.conf']

> depends_on: [api, web]

**10.2 Nginx routing rules**

-   /api/* → proxy_pass http://api:8000 --- all REST API traffic

-   /ws/* → proxy_pass http://api:8000 with Upgrade + Connection headers --- WebSocket

-   /* → proxy_pass http://web:80 --- React SPA (catch-all)

-   /docs → proxy_pass http://api:8000/docs --- FastAPI Swagger UI

**10.3 Running the full stack locally**

> docker compose up --build

> # API: http://localhost:8000

> # Swagger UI: http://localhost:8000/docs

> # React app: http://localhost:3000

> # Full stack: http://localhost:80 (via Nginx)

**11. Migration Roadmap**

  -------------- ------------------------------ ------------ ----------------------------------------------------------------------------------------------------------------
  **Phase**      **Name**                       **Effort**   **Scope**

  **Phase 1**    **Service layer extraction**   1--2 days    Copy calculate_*, fetch_*, parse_* from app.py into services/; verify all imports work without Streamlit

  **Phase 2**    **FastAPI scaffold**           1 day        main.py, routers, Pydantic models, Redis client; GET /api/health returns {status: ok}

  **Phase 3**    **Jolpica REST routes**        3--4 days    Wire standings, races, qualifying, laps; test with Swagger UI at /docs

  **Phase 4**    **Analytics REST routes**      2--3 days    All 15 analytics endpoints; Pydantic responses; pytest coverage ≥ 80%

  **Phase 5**    **OpenF1 REST routes**         2 days       All /api/live/* endpoints; session resolver; driver registry

  **Phase 6**    **WebSocket server**           2--3 days    ConnectionManager; /ws/live broadcast loop; /ws/telemetry per-driver stream

  **Phase 7**    **React scaffold**             1--2 days    Vite + TypeScript + Tailwind; React Router; Axios client; React Query

  **Phase 8**    **Historical tabs (1--9)**     4--5 days    Port each Streamlit tab to React page; Plotly via react-plotly.js

  **Phase 9**    **Advanced Analytics tab**     3--4 days    5 sub-section pages; radar, percentile, trend components

  **Phase 10**   **Live Race Tracker**          4--5 days    WebSocket hook; all 7 panels; mode detection; tyre colour mapping

  **Phase 11**   **Docker + Nginx**             1--2 days    docker-compose.yml; nginx.conf; .env files; production build

  **Phase 12**   **Testing + polish**           3--4 days    pytest-asyncio; Vitest; mobile layout; error and empty states
  -------------- ------------------------------ ------------ ----------------------------------------------------------------------------------------------------------------

Total estimated effort: 4--6 weeks part-time. Phase 1 (service layer extraction) is the most critical first step --- once complete, the FastAPI backend can be developed and tested independently of any frontend work. The existing Streamlit app continues running during the entire migration.

**12. Full Dependency List**

  ---------------------------- ------------- -------------------------------------------------------------
  **Package**                  **Version**   **Purpose**

  **── BACKEND ──**                         

  **fastapi**                  ≥ 0.110       Web framework; async routes; WebSocket support built-in

  **uvicorn[standard]**      ≥ 0.28        ASGI server; websockets extra required for WS support

  **pydantic**                 v2 ≥ 2.6      Request/response validation; auto Swagger docs generation

  **httpx**                    ≥ 0.27        Async HTTP client for Jolpica + OpenF1 API calls

  **redis[asyncio]**         ≥ 5.0         Async Redis client; shared caching layer

  **pandas**                   ≥ 2.0         DataFrames for all analytics calculations

  **numpy**                    ≥ 1.26        Vectorised stats: std_dev, correlation, regression

  **scipy**                    ≥ 1.11        Pearson correlation; trend slope classification

  **pytest**                   ≥ 7.0         Unit test runner

  **pytest-asyncio**           ≥ 0.23        Async test support for FastAPI route tests

  **hypothesis**               ≥ 6.0         Property-based testing; 26 analytics correctness properties

  **── FRONTEND ──**                         

  **react**                    ≥ 18.0        UI framework

  **typescript**               ≥ 5.0         Type safety across all components and API calls

  **vite**                     ≥ 5.0         Build tool; dev server with HMR

  **react-router-dom**         ≥ 6.0         Client-side routing for all 11 pages

  **@tanstack/react-query**   ≥ 5.0         Server state: API calls, caching, background refresh

  **zustand**                  ≥ 4.0         Client state: WebSocket data, session info, user prefs

  **axios**                    ≥ 1.6         Typed HTTP client for REST API calls

  **react-plotly.js**          ≥ 2.6         Plotly charts; accepts same figure config as Python

  **tailwindcss**              ≥ 3.4         Utility-first CSS; responsive layout

  **vitest**                   ≥ 1.0         Frontend unit test runner

  **── INFRASTRUCTURE ──**                   

  **docker**                   ≥ 24.0        Container runtime

  **docker compose**           ≥ 2.24        Orchestrates api + web + redis + nginx

  **nginx**                    ≥ 1.25        Reverse proxy; routes /api, /ws, and /* correctly

  **redis**                    ≥ 7.2         In-memory cache; shared across all API workers
  ---------------------------- ------------- -------------------------------------------------------------

**13. Key Architectural Decisions**

**Why httpx over requests**

FastAPI is async. The synchronous requests library blocks the event loop inside async handlers, eliminating all concurrency. httpx provides an identical API with full async/await support and shared connection pooling across requests.

**Why Redis over in-process caching**

@st.cache_data stored results in the single Streamlit process --- fine for one user. Redis is an external shared cache that works correctly across multiple Uvicorn workers, horizontal replicas, and restarts. TTL invalidation is reliable and consistent.

**Why Zustand over Redux for WebSocket state**

Redux requires action creators, reducers, and middleware for what is essentially a few simple state slices. Zustand provides the same predictable updates with a fraction of the boilerplate. The WebSocket onmessage handler writes directly to the store in three lines.

**Why react-plotly.js**

The backend already produces Plotly figure configs in Python. Returning those configs from the API and passing them to react-plotly.js means zero chart logic needs to be rewritten in TypeScript. All create_analytics_* functions are reused as-is on the backend.

**Why Nginx in front of both services**

A single entry point on port 80 means the React app and API share the same origin, eliminating CORS complexity in production. Without Nginx, every API call from React at :3000 to FastAPI at :8000 requires CORS headers --- which work but add noise and failure modes.

**Why not GraphQL**

The F1 dashboard has well-defined, stable query shapes. GraphQL's flexibility adds schema design, resolver complexity, and client query management without a meaningful benefit for this use case. FastAPI's auto-generated Swagger UI provides better developer experience for a REST API.

*F1 Dashboard --- FastAPI + React Architecture · v2.0 · March 2026*