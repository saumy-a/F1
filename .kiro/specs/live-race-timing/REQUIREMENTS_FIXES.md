# Requirements Document Fixes - Applied

## Date: 2026-03-22

All 6 critical issues have been fixed in the requirements document.

## Fix 1: Replay Endpoint URL Style ✅
**Issue**: Requirements used query param style `/api/live/positions?session_key=X` but backend uses path param style `/api/live/positions/{session_key}`

**Fix Applied**: Updated all replay mode endpoints in Requirement 4 (R4.5-R4.10):
- `/api/live/positions/{selected_key}`
- `/api/live/intervals/{selected_key}`
- `/api/live/race-control/{selected_key}`
- `/api/live/weather/{selected_key}`
- `/api/live/pits/{selected_key}`
- `/api/live/stints/{selected_key}`

## Fix 2: /api/live/sessions Endpoint ✅
**Issue**: Session selector called `/api/live/sessions` which doesn't exist in backend

**Fix Applied**: Updated Requirement 22 (R22.1):
- Changed from: `/api/live/sessions endpoint`
- Changed to: `OpenF1 API at https://api.openf1.org/v1/sessions?year={year}`
- Frontend will call OpenF1 directly for session list

## Fix 3: HARD Tyre Color ✅
**Issue**: Requirements said "white" for HARD compound, but white on white background is invisible

**Fix Applied**: Updated Requirement 8 (R8.4):
- Changed from: "white for HARD compound"
- Changed to: "grey (#CCCCCC) for HARD compound"
- Matches the steering file specification

## Fix 4: Gap to Leader Null Handling ✅
**Issue**: Requirements didn't specify how to handle null (P1) and "+1 LAP" string values

**Fix Applied**: Updated Requirement 6 (R6.3):
- Added: "(P1 displays '—', lapped cars display '+1 LAP' as-is)"
- Prevents crashes from calling `.toFixed()` on null or string values

## Fix 5: Remove Transcript Requirement ✅
**Issue**: R12.6 mentioned transcript text, but OpenF1 only provides audio URLs

**Fix Applied**: Removed Requirement 12.6:
- Deleted: "THE Team_Radio_Player SHALL display transcript text when available"
- Renumbered subsequent requirements (R12.7 → R12.6, R12.8 → R12.7, etc.)

## Fix 6: Endpoint Naming Consistency ✅
**Issue**: Inconsistent use of "racecontrol" vs "race-control" throughout document

**Fix Applied**: Global standardization to "race-control":
- R4.7: `/api/live/race-control/{selected_key}`
- R11.11: Added explicit endpoint reference `/api/live/race-control`
- R21.8: `/api/live/grid/{session_key}` (also fixed to use path param)
- TypeScript interface name remains `RaceControl` (camelCase for code)

## Verification

All fixes have been applied and verified:
- ✅ All replay endpoints use path param style `/{session_key}`
- ✅ Session selector calls OpenF1 API directly
- ✅ HARD tyre color is grey (#CCCCCC)
- ✅ Gap to leader null handling specified
- ✅ Transcript requirement removed
- ✅ All endpoints use "race-control" consistently

## Next Steps

The requirements document is now ready for the design phase. All endpoint URLs match the backend implementation pattern, and all data handling edge cases are properly specified.
