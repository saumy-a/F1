import { test, expect } from '@playwright/test'

test.describe('Overview Page', () => {
  test('Overview page loads and displays dashboard', async ({ page }) => {
    await page.goto('/')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('F1 Dashboard')
    
    // Check for main sections
    await expect(page.getByText('Next Race')).toBeVisible()
    await expect(page.getByText('Latest Results')).toBeVisible()
    await expect(page.getByText('Championship Leaders')).toBeVisible()
  })

  test('Overview page shows current year by default', async ({ page }) => {
    await page.goto('/')
    
    // Check year selector shows 2026 (current year)
    const selectedYear = await page.locator('select').inputValue()
    expect(selectedYear).toBe('2026')
  })

  test('Overview page has working links', async ({ page }) => {
    await page.goto('/')
    
    // Click on a standings link
    await page.click('text=View Full Standings')
    
    // Should navigate to standings page
    await expect(page).toHaveURL(/\/standings/)
  })
})
