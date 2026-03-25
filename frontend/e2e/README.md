# End-to-End Tests with Playwright

This directory contains comprehensive end-to-end tests for the F1 Dashboard application using Playwright.

## Test Coverage

### 1. Navigation Tests (`navigation.spec.ts`)
- ✅ Navigate to all 11 pages from header
- ✅ Year selector persists across pages
- ✅ URL routing works correctly

### 2. Standings Tests (`standings.spec.ts`)
- ✅ Driver Standings page loads and displays data
- ✅ Constructor Standings page loads and displays data
- ✅ Year selector updates standings
- ✅ Tables display correct columns
- ✅ Charts render correctly

### 3. Race Tests (`races.spec.ts`)
- ✅ Calendar page displays race schedule
- ✅ Races page displays race results
- ✅ Qualifying page displays qualifying results
- ✅ Lap Times page displays lap time analysis
- ✅ Race selectors work correctly

### 4. Analytics Tests (`analytics.spec.ts`)
- ✅ Analytics page loads with 4 tabs
- ✅ Driver Analytics tab works
- ✅ Comparative Analytics tab works
- ✅ Handles insufficient data gracefully
- ✅ Driver selector works
- ✅ Multi-driver comparison works

### 5. Overview Tests (`overview.spec.ts`)
- ✅ Overview page loads dashboard
- ✅ Shows current year by default
- ✅ Links work correctly

### 6. Live Tracker Tests (`live-tracker.spec.ts`)
- ✅ Live Tracker page loads
- ✅ Shows appropriate message when no session active
- ✅ Session info displays correctly

## Running Tests

### Run all tests
```bash
npm run test:e2e
```

### Run tests in UI mode (interactive)
```bash
npm run test:e2e:ui
```

### Run specific test file
```bash
npx playwright test standings.spec.ts
```

### Run tests in headed mode (see browser)
```bash
npx playwright test --headed
```

### Run tests in debug mode
```bash
npx playwright test --debug
```

### View test report
```bash
npm run test:e2e:report
```

## Test Configuration

Tests are configured in `playwright.config.ts`:
- **Base URL:** http://localhost:5173
- **Browser:** Chromium (Chrome)
- **Retries:** 2 (in CI), 0 (locally)
- **Screenshots:** On failure only
- **Trace:** On first retry
- **Web Server:** Automatically starts dev server

## Prerequisites

1. **Backend must be running:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Redis must be running:**
   ```bash
   redis-server
   ```

3. **Frontend dev server** (automatically started by Playwright):
   ```bash
   npm run dev
   ```

## Test Structure

Each test file follows this pattern:
```typescript
import { test, expect } from '@playwright/test'

test.describe('Feature Name', () => {
  test('specific test case', async ({ page }) => {
    await page.goto('/path')
    await expect(page.locator('selector')).toBeVisible()
  })
})
```

## Debugging Failed Tests

1. **Check screenshots:** `playwright-report/` directory
2. **Check traces:** Open trace viewer with `npx playwright show-trace trace.zip`
3. **Run in headed mode:** See what's happening in the browser
4. **Use debug mode:** Step through tests interactively

## CI/CD Integration

Tests can be run in CI/CD pipelines:
```yaml
- name: Install Playwright
  run: npx playwright install --with-deps

- name: Run E2E tests
  run: npm run test:e2e
```

## Best Practices

1. **Wait for elements:** Use `await expect().toBeVisible()` instead of `waitForTimeout`
2. **Use data-testid:** For stable selectors
3. **Test user flows:** Not implementation details
4. **Keep tests independent:** Each test should work in isolation
5. **Use page objects:** For complex pages (future enhancement)

## Coverage

- **Total Tests:** 20+
- **Pages Covered:** 11/11 (100%)
- **Key Features:** Navigation, Data Loading, Charts, Forms, Error Handling
- **Browsers:** Chromium (can add Firefox, WebKit)

## Future Enhancements

- [ ] Add visual regression tests
- [ ] Add performance tests
- [ ] Add accessibility tests
- [ ] Add mobile viewport tests
- [ ] Add cross-browser tests (Firefox, Safari)
- [ ] Add API mocking for deterministic tests
