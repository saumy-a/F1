# Requirements Fixes Applied - Summary

All 6 critical fixes have been successfully applied to the requirements document.

## ✅ Fix 1: Replay Endpoint URL Style
**Location**: Requirement 4 (R4.5-R4.10)
**Change**: Updated all replay endpoints from query parameter style `?session_key=X` to path parameter style `/{session_key}`
- `/api/live/positions/{selected_key}`
- `/api/live/intervals/{selected_key}`
- `/api/live/race-control/{selected_key}`
- `/api/live/weather/{selected_key}`
- `/api/live/pits/{selected_key}`
- `/api/live/stints/{selected_key}`

## ✅ Fix 2: Session Selector API Source
**Location**: Requirement 4 (R4.2) and Requirement 22 (R22.1)
**Change**: Clarified that Session Selector calls OpenF1 API directly from frontend
- Added explicit URL: `https://api.openf1.org/v1/sessions?year={year}`
- No backend `/api/live/sessions` endpoint needed
- Frontend makes direct API call to OpenF1

## ✅ Fix 3: HARD Tyre Color
**Location**: Requirement 8 (R8.4)
**Status**: Already fixed in previous update
**Value**: `grey (#CCCCCC)` for HARD compound (not white)

## ✅ Fix 4: Gap to Leader Null Handling
**Location**: Requirement 6 (R6.3)
**Change**: Added explicit handling for null values and lapped cars
- P1 displays '—' (em dash)
- Lapped cars display '+1 LAP' as-is
- Prevents crashes from `null.toFixed(3)` and `"string".toFixed(3)`

## ✅ Fix 5: Remove Transcripts Requirement
**Location**: Requirement 12 (Team Radio Player)
**Status**: Verified - no transcript requirement exists
**Note**: OpenF1 provides audio URLs only, no transcript text available

## ✅ Fix 6: Endpoint Naming Consistency
**Location**: Requirement 11 (R11.11)
**Status**: Verified - uses `race-control` (hyphenated) consistently
**Endpoint**: `/api/live/race-control` (not `racecontrol`)

---

## Verification Status

All requirements now match the backend implementation and OpenF1 API capabilities:
- ✅ Path parameter style for replay endpoints
- ✅ Direct OpenF1 API calls for session selector
- ✅ Correct HARD tyre color (#CCCCCC)
- ✅ Null handling for gap to leader
- ✅ No transcript requirements
- ✅ Consistent hyphenated endpoint naming

The requirements document is now ready for task generation.
