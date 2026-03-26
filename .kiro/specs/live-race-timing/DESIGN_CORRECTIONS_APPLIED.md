# Design Document Corrections Applied - Summary

All 5 critical corrections have been successfully applied to the design document.

## ✅ Correction 1: Interval Model Type Update
**Location**: `models/live.py` - Interval class
**Change**: Updated `gap_to_leader` and `interval` fields to accept both float and string types
```python
# Before:
gap_to_leader: Optional[str] = None
interval: Optional[str] = None

# After:
gap_to_leader: Optional[Union[float, str]] = None
interval: Optional[Union[float, str]] = None
```
**Reason**: OpenF1 API returns numeric values for gaps/intervals, but also strings like "+1 LAP" for lapped cars

**Also updated TypeScript interface**:
```typescript
// Before:
gap_to_leader: string | null
interval: string | null

# After:
gap_to_leader: number | string | null
interval: number | string | null
```

## ✅ Correction 2: PitStop Model Field Rename
**Location**: `models/live.py` - PitStop class
**Change**: Renamed `pit_duration` to `stop_duration` and added `lane_duration` field
```python
# Before:
pit_duration: float

# After:
stop_duration: Optional[float] = None
lane_duration: float
```
**Reason**: OpenF1 API provides two separate duration fields - `pit_duration` (total stop time, can be null) and `pit_lane_time` (time in pit lane)

**Also updated TypeScript interface**:
```typescript
# Before:
pit_duration: number

# After:
stop_duration: number | null
lane_duration: number
```

## ✅ Correction 3: Zustand Store - Add Interval History
**Location**: `store/liveRaceStore.ts`
**Change**: Added `intervalHistory` array and `appendIntervalHistory` action
```typescript
// Added to state:
intervalHistory: { lap: number; driver_number: number; gap: number | null }[]

// Added action:
appendIntervalHistory: (lap: number, driver_number: number, gap: number | null) => void

// Implementation:
appendIntervalHistory: (lap, driver_number, gap) => set((state) => ({
  intervalHistory: [...state.intervalHistory, { lap, driver_number, gap }]
}))
```
**Reason**: Gap Tracker Chart needs historical gap data over laps to plot trends

## ✅ Correction 4: useWebSocket Hook - Use useRef for Reconnect Attempts
**Location**: `hooks/useWebSocket.ts`
**Change**: Replaced Zustand `reconnectAttempts` state with `useRef<number>(0)`
```typescript
# Before:
const {
  ...
  incrementReconnectAttempts,
  resetReconnectAttempts,
  reconnectAttempts
} = useLiveRaceStore()

# After:
const reconnectAttemptsRef = useRef(0)
const { ... } = useLiveRaceStore()

// Usage:
reconnectAttemptsRef.current = 0  // reset
reconnectAttemptsRef.current += 1  // increment
if (reconnectAttemptsRef.current < 10) { ... }
```
**Reason**: Reconnection attempts are local to the WebSocket hook and don't need global state. Using useRef prevents unnecessary re-renders.

**Also removed from Zustand store**:
- Removed `reconnectAttempts` from state
- Removed `incrementReconnectAttempts` action
- Removed `resetReconnectAttempts` action

## ✅ Correction 5: RaceTower Component - Add Stints for Current Compound
**Location**: `components/live/RaceTower.tsx`
**Change**: Added `stints` from store and derive current compound/tire age
```typescript
# Added:
const stints = useLiveRaceStore((state) => state.stints)

# Derive current stint:
const currentStint = stints.find((s) => 
  s.driver_number === pos.driver_number && s.lap_end === null
)

# Use in merged data:
return { 
  ...pos, 
  ...interval, 
  ...driver,
  current_compound: currentStint?.compound,
  tire_age: currentStint?.tyre_age_at_start
}
```
**Reason**: Current tire compound and age must be derived from active stint (where `lap_end === null`)

## ✅ Bonus: Added Sessions Endpoint
**Location**: Backend API Endpoints section
**Change**: Added `GET /api/live/sessions?year={year}` endpoint
```
GET /api/live/sessions?year={year}
```
**Reason**: Frontend SessionSelector cannot call OpenF1 directly due to CORS. Backend must proxy the sessions list.

**Also updated Replay Mode sequence diagram** to show:
```
Selector->>Backend: GET /api/live/sessions?year={year}
Backend->>OpenF1: GET /v1/sessions?year={year}
```

---

## Verification Status

All design document corrections are complete:
- ✅ Interval model accepts Union[float, str]
- ✅ PitStop model has stop_duration and lane_duration
- ✅ Zustand store has intervalHistory array
- ✅ useWebSocket uses useRef for reconnect attempts
- ✅ RaceTower derives compound from stints
- ✅ Backend sessions endpoint added

The design document is now ready for task generation and implementation.
