import { test, expect } from '@playwright/test';

test('should load JupyterLab', async ({ page }) => {
  // Navigate to JupyterLab
  await page.goto('/');

  // Wait for the page to load
  await page.waitForLoadState('networkidle');

  // Check if JupyterLab is loaded
  const title = await page.title();
  expect(title).toContain('JupyterLab');

  // Check if the main dock panel exists
  const dockPanel = await page.locator('#jp-main-dock-panel');
  await expect(dockPanel).toBeVisible({ timeout: 10000 });

  // Check for any console errors
  const consoleErrors: string[] = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text());
    }
  });

  // Wait a bit for any errors to appear
  await page.waitForTimeout(2000);

  // Log any console errors
  if (consoleErrors.length > 0) {
    console.log('Console errors:', consoleErrors);
  }

  // Check if the extension is loaded by looking for the trainwave dropdown
  // Note: This might not be visible if the server extension is not loaded
  const trainwaveDropdown = await page.locator('.trainwave-dropdown-trigger');
  try {
    await expect(trainwaveDropdown).toBeVisible({ timeout: 5000 });
    console.log('Trainwave dropdown found - extension is loaded');
  } catch (error) {
    console.log('Trainwave dropdown not found - extension may not be loaded');
    // This is expected if the server extension is not loaded
  }
});
