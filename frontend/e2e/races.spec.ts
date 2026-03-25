import { test, expect } from '@playwright/test'

test.describe('Race Pages', () => {
  test('Calendar page displays race schedule', async ({ page }) => {
    await page.goto('/calendar')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Race Calendar')
    
    // Check table has data
    const tableRows = page.locator('tbody tr')
    await expect(tableRows).not.toHaveCount(0)
    
    // Check for expected columns
    await expect(page.getByText('Round')).toBeVisible()
    await expect(page.getByText('Race Name')).toBeVisible()
    await expect(page.getByText('Circuit')).toBeVisible()
    await expect(page.getByText('Date')).toBeVisible()
  })

  test('Races page displays race results', async ({ page }) => {
    await page.goto('/races')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Race Results')
    
    // Select a race
    await page.selectOption('select', { index: 1 })
    
    // Wait for results to load
    await page.waitForTimeout(1000)
    
    // Check results table appears
    const tableRows = page.locator('tbody tr')
    await expect(tableRows).not.toHaveCount(0)
  })

  test('Qualifying page displays qualifying results', async ({ page }) => {
    await page.goto('/qualifying')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Qualifying Results')
    
    // Select a race
    await page.selectOption('select', { index: 1 })
    
    // Wait for results to load
    await page.waitForTimeout(1000)
    
    // Check results table appears
    const tableRows = page.locator('tbody tr')
    await expect(tableRows).not.toHaveCount(0)
  })

  test('Lap Times page displays lap time analysis', async ({ page }) => {
    await page.goto('/lap-times')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Lap Times')
    
    // Select a race
    await page.selectOption('select[name="race"]', { index: 1 })
    
    // Wait for data to load
    await page.waitForTimeout(1000)
    
    // Check chart appears
    await expect(page.locator('.js-plotly-plot')).toBeVisible()
  })
})
