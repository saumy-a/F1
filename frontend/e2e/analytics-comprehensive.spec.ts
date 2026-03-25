import { test, expect } from '@playwright/test'

test.describe('Analytics Page - Comprehensive Testing', () => {
  test.beforeEach(async ({ page }) => {
    // Enable console and error logging
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('CONSOLE ERROR:', msg.text())
      }
    })
    page.on('pageerror', err => console.log('PAGE ERROR:', err.message))
    
    await page.goto('http://localhost:5173/analytics')
    await page.waitForLoadState('networkidle')
  })

  test('Page loads with correct title and tabs', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Advanced Analytics')
    
    // Check all tabs are present
    await expect(page.getByRole('button', { name: 'Driver Analytics' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Team Analytics' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Circuit Analytics' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Comparative Analytics' })).toBeVisible()
  })

  test('Driver Analytics - Driver selection works', async ({ page }) => {
    // Should show driver selector
    await expect(page.locator('select').first()).toBeVisible()
    
    // Should show placeholder message initially
    await expect(page.getByText('Please select a driver')).toBeVisible()
    
    // Select a driver
    await page.locator('select').first().selectOption({ index: 1 })
    
    // Wait for API calls
    await page.waitForTimeout(2000)
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'test-results/analytics-driver-selected.png' })
  })

  test('Driver Analytics - Performance Trends section', async ({ page }) => {
    // Select a driver
    await page.locator('select').first().selectOption({ index: 1 })
    await page.waitForTimeout(2000)
    
    // Check if Performance Trends section appears
    const performanceTrends = page.getByText('Performance Trends')
    const isVisible = await performanceTrends.isVisible().catch(() => false)
    
    if (isVisible) {
      console.log('✓ Performance Trends section is visible')
      // Check for chart
      const hasChart = await page.locator('[class*="plotly"]').count() > 0
      console.log('Has Plotly chart:', hasChart)
    } else {
      console.log('✗ Performance Trends section NOT visible - BUG CONFIRMED')
      // Log what sections ARE visible
      const sections = await page.locator('h2').allTextContents()
      console.log('Visible sections:', sections)
    }
  })

  test('Driver Analytics - Consistency Score section', async ({ page }) => {
    // Select a driver
    await page.locator('select').first().selectOption({ index: 1 })
    await page.waitForTimeout(2000)
    
    // Check for Consistency Score OR insufficient data message
    const consistencyScore = page.getByText('Consistency Score')
    const insufficientData = page.getByText('Insufficient data')
    
    const hasScore = await consistencyScore.isVisible().catch(() => false)
    const hasWarning = await insufficientData.isVisible().catch(() => false)
    
    if (hasScore) {
      console.log('✓ Consistency Score section is visible')
    } else if (hasWarning) {
      console.log('✓ Insufficient data warning shown (expected for early season)')
    } else {
      console.log('✗ Neither Consistency Score nor warning visible - BUG CONFIRMED')
    }
  })

  test('Driver Analytics - Form Indicator section', async ({ page }) => {
    // Select a driver
    await page.locator('select').first().selectOption({ index: 1 })
    await page.waitForTimeout(2000)
    
    const formIndicator = page.getByText('Recent Form')
    const isVisible = await formIndicator.isVisible().catch(() => false)
    
    if (isVisible) {
      console.log('✓ Recent Form section is visible')
      // Check for trend indicator
      const hasTrend = await page.getByText(/improving|declining|stable/i).isVisible().catch(() => false)
      console.log('Has trend indicator:', hasTrend)
    } else {
      console.log('✗ Recent Form section NOT visible - BUG CONFIRMED')
    }
  })

  test('Driver Analytics - DNF Statistics section', async ({ page }) => {
    // Select a driver
    await page.locator('select').first().selectOption({ index: 1 })
    await page.waitForTimeout(2000)
    
    const dnfStats = page.getByText('DNF Statistics')
    const isVisible = await dnfStats.isVisible().catch(() => false)
    
    if (isVisible) {
      console.log('✓ DNF Statistics section is visible')
    } else {
      console.log('✗ DNF Statistics section NOT visible - BUG CONFIRMED')
    }
  })

  test('Team Analytics - Shows placeholder', async ({ page }) => {
    await page.click('text=Team Analytics')
    await page.waitForTimeout(500)
    
    await expect(page.getByText(/coming soon/i)).toBeVisible()
    console.log('✓ Team Analytics placeholder confirmed')
  })

  test('Circuit Analytics - Shows placeholder', async ({ page }) => {
    await page.click('text=Circuit Analytics')
    await page.waitForTimeout(500)
    
    await expect(page.getByText(/coming soon/i)).toBeVisible()
    console.log('✓ Circuit Analytics placeholder confirmed')
  })

  test('Comparative Analytics - Driver selection works', async ({ page }) => {
    await page.click('text=Comparative Analytics')
    await page.waitForTimeout(500)
    
    // Should show checkboxes
    const checkboxes = await page.locator('input[type="checkbox"]').count()
    expect(checkboxes).toBeGreaterThan(0)
    console.log(`✓ Found ${checkboxes} driver checkboxes`)
    
    // Should show placeholder message initially
    await expect(page.getByText('Please select at least 2 drivers')).toBeVisible()
  })

  test('Comparative Analytics - Comparison works with 2 drivers', async ({ page }) => {
    await page.click('text=Comparative Analytics')
    await page.waitForTimeout(500)
    
    // Select 2 drivers
    await page.locator('input[type="checkbox"]').nth(0).check()
    await page.locator('input[type="checkbox"]').nth(1).check()
    
    // Wait for API call
    await page.waitForTimeout(2000)
    
    // Check for comparison sections
    const multiDimensional = page.getByText('Multi-Dimensional Comparison')
    const sideBySide = page.getByText('Side-by-Side Metrics')
    const projection = page.getByText('Championship Projection')
    
    const hasMulti = await multiDimensional.isVisible().catch(() => false)
    const hasSide = await sideBySide.isVisible().catch(() => false)
    const hasProj = await projection.isVisible().catch(() => false)
    
    console.log('Multi-Dimensional Comparison:', hasMulti ? '✓' : '✗')
    console.log('Side-by-Side Metrics:', hasSide ? '✓' : '✗')
    console.log('Championship Projection:', hasProj ? '✓' : '✗')
    
    if (hasMulti && hasSide && hasProj) {
      console.log('✓ All comparison sections visible')
    } else {
      console.log('✗ Some comparison sections missing')
    }
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/analytics-comparison.png', fullPage: true })
  })

  test('Comparative Analytics - Driver limit enforcement', async ({ page }) => {
    await page.click('text=Comparative Analytics')
    await page.waitForTimeout(500)
    
    // Try to select 6 drivers (should only allow 5)
    for (let i = 0; i < 6; i++) {
      const checkbox = page.locator('input[type="checkbox"]').nth(i)
      const isEnabled = await checkbox.isEnabled()
      if (isEnabled) {
        await checkbox.check()
      }
    }
    
    // Count checked boxes
    const checkedCount = await page.locator('input[type="checkbox"]:checked').count()
    expect(checkedCount).toBeLessThanOrEqual(5)
    console.log(`✓ Driver limit enforced: ${checkedCount} of 5 max selected`)
  })

  test('API Error Handling - Network failure', async ({ page }) => {
    // Intercept API calls and make them fail
    await page.route('**/api/analytics/**', route => route.abort())
    
    await page.goto('http://localhost:5173/analytics')
    await page.waitForTimeout(1000)
    
    // Select a driver
    await page.locator('select').first().selectOption({ index: 1 })
    await page.waitForTimeout(2000)
    
    // Should show error message
    const errorMessage = page.getByText(/failed to load/i)
    const hasError = await errorMessage.isVisible().catch(() => false)
    
    if (hasError) {
      console.log('✓ Error message displayed on API failure')
    } else {
      console.log('✗ No error message on API failure - ERROR HANDLING BUG')
    }
  })

  test('Loading States - Shows spinner while loading', async ({ page }) => {
    // This test checks if loading states are properly shown
    await page.goto('http://localhost:5173/analytics')
    
    // Check for loading spinner during initial load
    const spinner = page.locator('[class*="loading"], [class*="spinner"]')
    const hasSpinner = await spinner.isVisible().catch(() => false)
    
    console.log('Loading spinner visible:', hasSpinner ? '✓' : '✗')
  })
})

test.describe('Overview Page - Comprehensive Testing', () => {
  test.beforeEach(async ({ page }) => {
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.log('CONSOLE ERROR:', msg.text())
      }
    })
    page.on('pageerror', err => console.log('PAGE ERROR:', err.message))
    
    await page.goto('http://localhost:5173/')
    await page.waitForLoadState('networkidle')
  })

  test('Page loads with correct title', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('F1 Dashboard Overview')
  })

  test('Next Race card displays', async ({ page }) => {
    const nextRaceCard = page.getByText('Next Race')
    await expect(nextRaceCard).toBeVisible()
    console.log('✓ Next Race card visible')
  })

  test('Latest Race card displays', async ({ page }) => {
    const latestRaceCard = page.getByText('Latest Race')
    await expect(latestRaceCard).toBeVisible()
    console.log('✓ Latest Race card visible')
  })

  test('Latest Results section - MISSING', async ({ page }) => {
    const latestResults = page.getByText('Latest Results')
    const isVisible = await latestResults.isVisible().catch(() => false)
    
    if (isVisible) {
      console.log('✓ Latest Results section found')
    } else {
      console.log('✗ Latest Results section MISSING - BUG CONFIRMED')
    }
  })

  test('Championship Leaders section - MISSING', async ({ page }) => {
    const champLeaders = page.getByText('Championship Leaders')
    const isVisible = await champLeaders.isVisible().catch(() => false)
    
    if (isVisible) {
      console.log('✓ Championship Leaders section found')
    } else {
      console.log('✗ Championship Leaders section MISSING - BUG CONFIRMED')
    }
  })

  test('Driver Standings preview displays', async ({ page }) => {
    const driverStandings = page.getByText('Driver Standings (Top 5)')
    await expect(driverStandings).toBeVisible()
    
    // Check if standings data is shown
    const hasData = await page.locator('text=/pts/').count() > 0
    console.log('Driver standings has data:', hasData ? '✓' : '✗')
  })

  test('Constructor Standings preview displays', async ({ page }) => {
    const constructorStandings = page.getByText('Constructor Standings (Top 3)')
    await expect(constructorStandings).toBeVisible()
    
    // Check if standings data is shown
    const hasData = await page.locator('text=/pts/').count() > 0
    console.log('Constructor standings has data:', hasData ? '✓' : '✗')
  })

  test('View Full Standings links - MISSING', async ({ page }) => {
    const viewFullLink = page.getByText('View Full Standings')
    const isVisible = await viewFullLink.isVisible().catch(() => false)
    
    if (isVisible) {
      console.log('✓ View Full Standings link found')
    } else {
      console.log('✗ View Full Standings link MISSING - BUG CONFIRMED')
    }
  })

  test('Navigation to standings pages', async ({ page }) => {
    // Try clicking on driver standings card
    const driverCard = page.locator('text=Driver Standings').first()
    const isClickable = await driverCard.isVisible()
    
    if (isClickable) {
      // Check if it's a link
      const isLink = await page.locator('a:has-text("Driver Standings")').count() > 0
      console.log('Driver standings is a link:', isLink ? '✓' : '✗')
    }
  })

  test('Screenshot - Full page', async ({ page }) => {
    await page.screenshot({ path: 'test-results/overview-full-page.png', fullPage: true })
    console.log('✓ Screenshot saved')
  })
})
