import { test, expect } from '@playwright/test'

test.describe('Live Tracker Page', () => {
  test('Live Tracker page loads', async ({ page }) => {
    await page.goto('/live')
    
    // Check page title
    await expect(page.locator('h1')).toContainText('Live Race Tracker')
    
    // Check for session info or no active session message
    const noSessionMessage = page.getByText(/No active session/i)
    const sessionInfo = page.getByText(/Session/i)
    
    // Either message should be visible
    const noSessionVisible = await noSessionMessage.isVisible().catch(() => false)
    const sessionInfoVisible = await sessionInfo.isVisible().catch(() => false)
    
    expect(noSessionVisible || sessionInfoVisible).toBeTruthy()
  })

  test('Live Tracker shows appropriate message when no session active', async ({ page }) => {
    await page.goto('/live')
    
    // Most likely no active F1 session during testing
    await expect(page.getByText(/No active session/i)).toBeVisible()
  })
})
