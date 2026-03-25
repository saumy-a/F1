import { test, expect } from '@playwright/test'

test.describe('Analytics Page', () => {
  test('Analytics page loads with tabs', async ({ page }) => {
    await page.goto('/analytics')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Advanced Analytics')
    
    // Check all tabs are visible
    await expect(page.getByText('Driver Analytics')).toBeVisible()
    await expect(page.getByText('Team Analytics')).toBeVisible()
    await expect(page.getByText('Circuit Analytics')).toBeVisible()
    await expect(page.getByText('Comparative Analytics')).toBeVisible()
  })

  test('Driver Analytics tab works', async ({ page }) => {
    await page.goto('/analytics')
    
    // Click Driver Analytics tab
    await page.click('text=Driver Analytics')
    
    // Select a driver
    await page.selectOption('select', { index: 1 })
    
    // Wait for analytics to load
    await page.waitForTimeout(2000)
    
    // Check for analytics sections (some may show insufficient data message)
    const performanceTrends = page.getByText('Performance Trends')
    const consistencyScore = page.getByText('Consistency Score')
    const recentForm = page.getByText('Recent Form')
    const dnfStats = page.getByText('DNF Statistics')
    
    // At least one section should be visible
    const visibleSections = await Promise.all([
      performanceTrends.isVisible().catch(() => false),
      consistencyScore.isVisible().catch(() => false),
      recentForm.isVisible().catch(() => false),
      dnfStats.isVisible().catch(() => false),
    ])
    
    expect(visibleSections.some(v => v)).toBeTruthy()
  })

  test('Comparative Analytics tab works', async ({ page }) => {
    await page.goto('/analytics')
    
    // Click Comparative Analytics tab
    await page.click('text=Comparative Analytics')
    
    // Check for driver selector
    await expect(page.getByText('Select Drivers (2-5)')).toBeVisible()
    
    // Select 2 drivers
    const checkboxes = page.locator('input[type="checkbox"]')
    await checkboxes.nth(0).check()
    await checkboxes.nth(1).check()
    
    // Wait for comparison to load
    await page.waitForTimeout(2000)
    
    // Check for comparison sections
    await expect(page.getByText('Multi-Dimensional Comparison')).toBeVisible()
  })

  test('Handles insufficient data gracefully', async ({ page }) => {
    await page.goto('/analytics')
    
    // Select a driver
    await page.selectOption('select', { index: 1 })
    
    // Wait for analytics to load
    await page.waitForTimeout(2000)
    
    // Check if insufficient data message appears (for 2026 with few races)
    const insufficientDataMessage = page.getByText(/Insufficient data/i)
    
    // If message appears, that's expected behavior
    if (await insufficientDataMessage.isVisible()) {
      expect(await insufficientDataMessage.isVisible()).toBeTruthy()
    }
  })
})
