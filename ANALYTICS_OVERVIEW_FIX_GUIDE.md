# Analytics & Overview Pages - Quick Fix Guide

## 🚀 Quick Start

This guide provides step-by-step instructions to fix all identified bugs in the Analytics and Overview pages.

---

## 📦 What You Need

1. **Bug Reports**:
   - `ANALYTICS_AND_OVERVIEW_BUG_REPORT.md` - Detailed bug analysis
   - `PLAYWRIGHT_COMPREHENSIVE_TEST_RESULTS.md` - Test results with all bugs confirmed

2. **Test Suite**:
   - `frontend/e2e/analytics-comprehensive.spec.ts` - 23 automated tests

3. **Run Tests**:
   ```bash
   cd frontend
   npm run test:e2e -- e2e/analytics-comprehensive.spec.ts
   ```

---

## 🔧 Fix #1: Data Structure Transformation (CRITICAL)

### Problem
Backend returns pandas DataFrame-like JSON, frontend expects array of objects.

### Solution
Create a data transformation utility:

```typescript
// frontend/src/utils/dataTransform.ts

export function transformPandasToArray<T>(data: any): T[] {
  if (!data || typeof data !== 'object') return []
  
  // Check if it's pandas format (object with numeric keys)
  const keys = Object.keys(data)
  if (keys.length === 0) return []
  
  const firstKey = keys[0]
  const firstValue = data[firstKey]
  
  if (typeof firstValue !== 'object') return []
  
  const indices = Object.keys(firstValue)
  
  return indices.map(index => {
    const row: any = {}
    keys.forEach(key => {
      row[key] = data[key][index]
    })
    return row as T
  })
}
```

### Usage in Analytics Hooks

Update `frontend/src/hooks/useAnalytics.ts`:

```typescript
import { transformPandasToArray } from '../utils/dataTransform'

export function usePerformanceTrends(driverId: string, year: string) {
  return useQuery({
    queryKey: ['performance-trends', driverId, year],
    queryFn: async () => {
      const response = await apiClient.get(
        `/api/analytics/trends/${driverId}/${year}`
      )
      
      // Transform pandas format to array
      const transformed = transformPandasToArray(response.data.data)
      
      return {
        data: transformed.map((row: any) => ({
          round: row.round,
          position: row.metric_value,
          race_name: row.race_name,
          race_date: row.race_date
        }))
      }
    },
    staleTime: 10 * 60 * 1000,
    enabled: !!driverId && !!year,
  })
}
```

---

## 🔧 Fix #2: Form Indicator Field Mapping (CRITICAL)

### Problem
Backend returns `trend_direction`, `avg_position`, frontend expects `trend`, `average_position`.

### Solution
Update `frontend/src/hooks/useAnalytics.ts`:

```typescript
export function useFormIndicator(driverId: string, year: string, lastN: number = 5) {
  return useQuery({
    queryKey: ['form-indicator', driverId, year, lastN],
    queryFn: async () => {
      const response = await apiClient.get<any>(
        `/api/analytics/form/${driverId}/${year}`,
        { params: { last_n: lastN } }
      )
      
      // Map backend fields to frontend format
      return {
        recent_positions: [], // TODO: Backend needs to return this
        trend: response.data.trend_direction as 'improving' | 'declining' | 'stable',
        average_position: response.data.avg_position
      }
    },
    staleTime: 10 * 60 * 1000,
    enabled: !!driverId && !!year,
  })
}
```

---

## 🔧 Fix #3: Add Latest Results Section (HIGH)

### Problem
Overview page missing "Latest Results" section.

### Solution
Update `frontend/src/pages/OverviewPage.tsx`:

```typescript
import { useRaceResults } from '../hooks/useRaces'

export default function OverviewPage() {
  // ... existing code ...
  
  // Get latest race results
  const latestRaceRound = latestRace?.round
  const { data: latestResults } = useRaceResults(selectedYear, latestRaceRound)
  
  return (
    <div className="p-6">
      {/* ... existing code ... */}
      
      {/* Add Latest Results Section */}
      <div className="mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Latest Results</h2>
          {latestResults && latestResults.length > 0 ? (
            <div className="space-y-2">
              {latestResults.slice(0, 3).map((result) => (
                <div key={result.position} className="flex justify-between items-center py-2 border-b">
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-gray-500 w-6">{result.position}</span>
                    <span className="font-medium">
                      {result.Driver.givenName} {result.Driver.familyName}
                    </span>
                  </div>
                  <span className="text-gray-600">{result.Constructor.name}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No results available</p>
          )}
        </div>
      </div>
      
      {/* ... rest of code ... */}
    </div>
  )
}
```

---

## 🔧 Fix #4: Add View Full Standings Links (MEDIUM)

### Problem
No links to navigate to full standings pages.

### Solution
Update `frontend/src/pages/OverviewPage.tsx`:

```typescript
import { Link } from 'react-router-dom'

// In Driver Standings card:
<div className="bg-white rounded-lg shadow p-6">
  <div className="flex justify-between items-center mb-4">
    <h2 className="text-xl font-semibold">Driver Standings (Top 5)</h2>
    <Link 
      to="/standings/drivers" 
      className="text-red-600 hover:text-red-700 text-sm font-medium"
    >
      View Full Standings →
    </Link>
  </div>
  {/* ... standings data ... */}
</div>

// In Constructor Standings card:
<div className="bg-white rounded-lg shadow p-6">
  <div className="flex justify-between items-center mb-4">
    <h2 className="text-xl font-semibold">Constructor Standings (Top 3)</h2>
    <Link 
      to="/standings/constructors" 
      className="text-red-600 hover:text-red-700 text-sm font-medium"
    >
      View Full Standings →
    </Link>
  </div>
  {/* ... standings data ... */}
</div>
```

---

## 🔧 Fix #5: Add Error Handling (MEDIUM)

### Problem
No error messages shown when API calls fail.

### Solution
Update `frontend/src/pages/AnalyticsPage.tsx`:

```typescript
function DriverAnalyticsSection({ driverId, year }: { driverId: string; year: string }) {
  const {
    data: trends,
    isLoading: trendsLoading,
    error: trendsError,
    refetch: refetchTrends
  } = usePerformanceTrends(driverId, year)
  
  // ... other hooks ...
  
  if (!driverId) {
    return (
      <div className="text-center py-12 text-gray-500">
        Please select a driver to view analytics
      </div>
    )
  }

  if (isLoading) return <LoadingSpinner />
  
  // Show error with retry button
  if (trendsError || formError || dnfError) {
    return (
      <div className="bg-red-50 border border-red-200 p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-red-800 mb-2">
          Failed to load driver analytics
        </h3>
        <p className="text-red-700 mb-4">
          There was an error loading the analytics data. Please try again.
        </p>
        <button
          onClick={() => {
            refetchTrends()
            // refetch other queries...
          }}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    )
  }
  
  // ... rest of component ...
}
```

---

## 🔧 Fix #6: Fix Comparative Analytics 500 Error (HIGH)

### Problem
Backend returns 500 error when comparing drivers.

### Solution
Check backend logs and fix the `/api/analytics/compare` endpoint:

```bash
# Check backend logs
cd backend
tail -f logs/app.log

# Look for errors in analytics.py
```

Likely issues:
- Missing data for selected drivers
- Database query error
- Data transformation error

---

## ✅ Testing Your Fixes

After each fix, run the test suite:

```bash
cd frontend
npm run test:e2e -- e2e/analytics-comprehensive.spec.ts --reporter=list
```

### Expected Results After All Fixes:
- All 23 tests should pass
- No "BUG CONFIRMED" messages in output
- All sections should show ✓ instead of ✗

---

## 📊 Progress Tracking

Use this checklist to track your progress:

### Analytics Page Fixes
- [ ] Fix #1: Data structure transformation utility
- [ ] Fix #2: Form indicator field mapping
- [ ] Fix #3: Performance trends data transformation
- [ ] Fix #4: DNF statistics rendering
- [ ] Fix #5: Error handling with retry
- [ ] Fix #6: Comparative analytics 500 error

### Overview Page Fixes
- [ ] Fix #7: Add Latest Results section
- [ ] Fix #8: Add Championship Leaders section
- [ ] Fix #9: Add View Full Standings links
- [ ] Fix #10: Fix loading spinner visibility

### Verification
- [ ] All Playwright tests pass
- [ ] No console errors
- [ ] Manual testing completed
- [ ] Screenshots look correct
- [ ] Performance is acceptable

---

## 🆘 Troubleshooting

### Tests Still Failing?

1. **Clear browser cache**:
   ```bash
   npx playwright test --headed --debug
   ```

2. **Check API responses**:
   ```bash
   curl http://localhost:8000/api/analytics/trends/max_verstappen/2026
   ```

3. **Check console errors**:
   - Open browser DevTools
   - Look for red errors
   - Check Network tab for failed requests

4. **Verify backend is running**:
   ```bash
   curl http://localhost:8000/health
   ```

---

## 📞 Need Help?

- **Bug Reports**: See `ANALYTICS_AND_OVERVIEW_BUG_REPORT.md`
- **Test Results**: See `PLAYWRIGHT_COMPREHENSIVE_TEST_RESULTS.md`
- **Test Suite**: `frontend/e2e/analytics-comprehensive.spec.ts`

---

## 🎉 Success!

When all fixes are complete:
1. All 23 tests pass ✓
2. No console errors ✓
3. All sections render correctly ✓
4. Error handling works ✓
5. Loading states show ✓

**You're done!** 🚀
