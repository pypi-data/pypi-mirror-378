import { test, expect } from '@playwright/test';

test('debug JupyterLab interface', async ({ page }) => {
  // Navigate to JupyterLab
  await page.goto('/');

  // Wait for the page to load
  await page.waitForLoadState('networkidle');

  // Wait for JupyterLab to load
  await page.waitForSelector('#jp-main-dock-panel');

  // Take a screenshot
  await page.screenshot({ path: 'debug-screenshot.png' });

  // Look for any buttons that might be the "Create New Notebook" button
  const buttons = await page.locator('button').all();
  console.log('Found buttons:', buttons.length);

  for (let i = 0; i < Math.min(buttons.length, 10); i++) {
    const text = await buttons[i].textContent();
    const title = await buttons[i].getAttribute('title');
    console.log(`Button ${i}: text="${text}", title="${title}"`);
  }

  // Look for elements with data-command attributes
  const commandElements = await page.locator('[data-command]').all();
  console.log('Found command elements:', commandElements.length);

  for (let i = 0; i < Math.min(commandElements.length, 10); i++) {
    const command = await commandElements[i].getAttribute('data-command');
    const text = await commandElements[i].textContent();
    console.log(`Command element ${i}: command="${command}", text="${text}"`);
  }
});
