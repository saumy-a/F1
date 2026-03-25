import { test, expect } from '@playwright/test'

test.describe('Standings Pages', () => {
  test('Driver Standings page loads and displays data', async ({ page }) => {
    await page.goto('/standings/drivers')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Driver Standings')
    
    // Check table headers
    await expect(page.getByText('Position')).toBeVisible()
    await expect(page.getByText('Driver')).toBeVisible()
    await expect(page.getByText('Nationality')).toBeVisible()
    await expect(page.getByText('Team')).toBeVisible()
    await expect(page.getByText('Points')).toBeVisible()
    await expect(page.getByText('Wins')).toBeVisible()
    
    // Check that data is loaded (table has rows)
    const tableRows = page.locator('tbody tr')
    await expect(tableRows).not.toHaveCount(0)
    
    // Check chart is visible
    await expect(page.locator('.js-plotly-plot')).toBeVisible()
  })

  test('Constructor Standings page loads and displays data', async ({ page }) => {
    await page.goto('/standings/constructors')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Constructor Standings')
    
    // Check table headers
    await expect(page.getByText('Position')).toBeVisible()
    await expect(page.getByText('Constructor')).toBeVisible()
    await expect(page.getByText('Nationality')).toBeVisible()
    await expect(page.getByText('Points')).toBeVisible()
    await expect(page.getByText('Wins')).toBeVisible()
    
    // Check that data is loaded
    const tableRows = page.locator('tbody tr')
    await expect(tableRows).not.toHaveCount(0)
    
    // Check chart is visible
    await expect(page.locator('.js-plotly-plot')).toBeVisible()
  })

  test('Year selector updates standings', async ({ page }) => {
    await page.goto('/standings/drivers')
    
    // Wait for initial data to load
    await page.waitForSelector('tbody tr')
    
    // Change year to 2025
    await page.selectOption('select', '2025')
    
    // Wait for data to update
    await page.waitForTimeout(1000)
    
    // Check that page title updated
    await expect(page.locator('h1')).toContainText('2025')
  })
})
