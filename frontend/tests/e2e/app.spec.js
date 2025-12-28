import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  // Use configured VITE_API_BASE_URL by default pointing to backend
  await page.goto(process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:5173/');
});

test('home page loads and shows dashboard', async ({ page }) => {
  await expect(page).toHaveTitle(/Unified/);
  const header = await page.locator('h1, h2, h3').first();
  await expect(header).toBeVisible();
});
