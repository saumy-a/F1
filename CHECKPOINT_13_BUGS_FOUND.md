# Checkpoint 13: Bugs Found and Fixes

## Critical Bugs Identified

### 1. **RacesPage - Invalid className usage**
**File:** `frontend/src/pages/RacesPage.tsx`
**Issue:** Column definition uses `className` as a function, but DataTable expects a string
**Line:** Column for "Fastest Lap"
```typescript
className: (row: typeof raceResult.Results[0]) => row.FastestLap?.rank === '1' ? 'text-purple-600 font-semibold' : ''
```
**Impact:** TypeScript error, conditional styling won't work

### 2. **Type Mismatch - round is string not number**
**Files:** Multiple pages (RacesPage, QualifyingPage, LapTimesPage)
**Issue:** `race.round` is typed as `string` but being used as `number` in state
**Impact:** Type errors, potential runtime issues

### 3. **Missing null/undefined checks**
**Files:** Multiple pages
**Issue:** Pages access nested properties without checking if parent exists
**Example:** `raceResult.Results[0]` used in type definitions before checking if raceResult exists

### 4. **DataTable doesn't handle conditional className**
**File:** `frontend/src/components/shared/DataTable.tsx`
**Issue:** DataTable only supports static className strings, not conditional logic per row

### 5. **Custom Tailwind classes not defined**
**Files:** Multiple pages
**Issue:** Using `text-f1-red`, `focus:ring-f1-red`, `focus:border-f1-red` but these might not be in Tailwind config

### 6. **Race schedule might be empty on initial load**
**Files:** RacesPage, QualifyingPage, LapTimesPage
**Issue:** `selectedRound` defaults to 1, but races might not be loaded yet

### 7. **Missing error boundaries**
**Issue:** If a component crashes, entire app might crash

## Fixes Required

### Priority 1 (Blocking)
1. Fix RacesPage className issue
2. Fix type mismatches (string vs number for round)
3. Add proper null checks

### Priority 2 (Important)
4. Enhance DataTable to support row-based conditional styling
5. Add Tailwind custom colors or replace with standard colors
6. Fix initial state issues with race selection

### Priority 3 (Nice to have)
7. Add error boundaries
8. Improve loading states
