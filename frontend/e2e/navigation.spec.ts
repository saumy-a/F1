import { test, expect } from '@playwright/test'

test.describe('Navigation', () => {
  test('can navigate to all pages from header', async ({ page }) => {
    await page.goto('/')
    
    // Test Overview page
    await expect(page.locator('h1')).toContainText('F1 Dashboard')
    
    // Navigate to Driver Standings
    await page.click('text=Driver Standings')
    await expect(page).toHaveURL(/\/standings\/drivers/)
    await expect(page.locator('h1')).toContainText('Driver Standings')
    
    // Navigate to Constructor Standings
    await page.click('text=Constructor Standings')
    await expect(page).toHaveURL(/\/standings\/constructors/)
    await expect(page.locator('h1')).toContainText('Constructor Standings')
    
    // Navigate to Calendar
    await page.click('text=Calendar')
    await expect(page).toHaveURL(/\/calendar/)
    await expect(page.locator('h1')).toContainText('Race Calendar')
    
    // Navigate to Races
    await page.click('text=Races')
    await expect(page).toHaveURL(/\/races/)
    await expect(page.locator('h1')).toContainText('Race Results')
    
    // Navigate to Qualifying
    await page.click('text=Qualifying')
    await expect(page).toHaveURL(/\/qualifying/)
    await expect(page.locator('h1')).toContainText('Qualifying Results')
    
    // Navigate to Championship
    await page.click('text=Championship')
    await expect(page).toHaveURL(/\/championship/)
    await expect(page.locator('h1')).toContainText('Championship')
    
    // Navigate to Lap Times
    await page.click('text=Lap Times')
    await expect(page).toHaveURL(/\/lap-times/)
    await expect(page.locator('h1')).toContainText('Lap Times')
    
    // Navigate to Head-to-Head
    await page.click('text=Head-to-Head')
    await expect(page).toHaveURL(/\/head-to-head/)
    await expect(page.locator('h1')).toContainText('Head-to-Head')
    
    // Navigate to Analytics
    await page.click('text=Analytics')
    await expect(page).toHaveURL(/\/analytics/)
    await expect(page.locator('h1')).toContainText('Advanced Analytics')
    
    // Navigate to Live Tracker
    await page.click('text=Live Tracker')
    await expect(page).toHaveURL(/\/live/)
    await expect(page.locator('h1')).toContainText('Live Race Tracker')
  })

  test('year selector persists across pages', async ({ page }) => {
    await page.goto('/')
    
    // Change year to 2025
    await page.selectOption('select', '2025')
    
    // Navigate to different page
    await page.click('text=Driver Standings')
    
    // Check year is still 2025
    const selectedYear = await page.locator('select').inputValue()
    expect(selectedYear).toBe('2025')
    
    // Check page shows 2025 data
    await expect(page.locator('h1')).toContainText('2025')
  })
})
