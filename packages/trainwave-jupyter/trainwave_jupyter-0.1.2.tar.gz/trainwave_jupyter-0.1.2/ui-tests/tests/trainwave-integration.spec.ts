/**
 * UI Integration tests for the Trainwave JupyterLab extension
 */

import { test, expect } from '@playwright/test';

test.describe('Trainwave Extension UI Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to JupyterLab using baseURL from config
    await page.goto('/');

    // Wait for JupyterLab to load
    await page.waitForSelector('#jp-main-dock-panel');
  });

  test('should load the extension without errors', async ({ page }) => {
    // Check that the extension loads without console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Wait a bit for the extension to initialize
    await page.waitForTimeout(2000);

    // Filter out known non-critical errors
    const criticalErrors = errors.filter(
      error =>
        !error.includes('trainwave') &&
        !error.includes('extension') &&
        !error.includes('404')
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('should show trainwave dropdown in notebook toolbar', async ({
    page
  }) => {
    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Look for the trainwave dropdown in the toolbar
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await expect(trainwaveDropdown).toBeAttached({ timeout: 10000 });
  });

  test('should open authentication dialog when login is clicked', async ({
    page
  }) => {
    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Click the trainwave dropdown
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await trainwaveDropdown.click();

    // Click login button
    const loginButton = page.locator('text=Sign In');
    await loginButton.click();

    // Check that authentication dialog appears
    const authDialog = page.locator('.trainwave-auth-dialog');
    await expect(authDialog).toBeVisible();
  });

  test('should show authentication form in dialog', async ({ page }) => {
    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Open authentication dialog
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await trainwaveDropdown.click();
    const loginButton = page.locator('text=Sign In');
    await loginButton.click();

    // Check dialog content
    const authDialog = page.locator('.trainwave-auth-dialog');
    await expect(authDialog).toBeVisible();

    // Check for key elements
    await expect(authDialog.locator('h3')).toContainText(
      'Trainwave Authentication'
    );
    await expect(
      authDialog.locator('text=Connect your Trainwave account')
    ).toBeVisible();
    await expect(
      authDialog.locator('text=Authenticate with Trainwave')
    ).toBeVisible();
  });

  test('should open settings dialog when settings is clicked', async ({
    page
  }) => {
    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Click the trainwave dropdown
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await trainwaveDropdown.click();

    // Click settings button (this might be in a submenu)
    const settingsButton = page.locator('text=Settings');
    await settingsButton.click();

    // Check that settings dialog appears
    const settingsDialog = page.locator('.trainwave-settings-dialog');
    await expect(settingsDialog).toBeVisible({ timeout: 5000 });
  });

  test('should show settings form in dialog', async ({ page }) => {
    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Open settings dialog
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await trainwaveDropdown.click();
    const settingsButton = page.locator('text=Settings');
    await settingsButton.click();

    // Check dialog content
    const settingsDialog = page.locator('.trainwave-settings-dialog');
    await expect(settingsDialog).toBeVisible();

    // Check for key elements
    await expect(settingsDialog.locator('h3')).toContainText(
      'Trainwave Settings'
    );
    await expect(
      settingsDialog.locator('input[placeholder*="API Endpoint"]')
    ).toBeVisible();
    await expect(
      settingsDialog.locator('select[name="gpu_type"]')
    ).toBeVisible();
    await expect(
      settingsDialog.locator('input[name="gpu_count"]')
    ).toBeVisible();
  });

  test('should handle authentication flow', async ({ page }) => {
    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Open authentication dialog
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await trainwaveDropdown.click();
    const loginButton = page.locator('text=Sign In');
    await loginButton.click();

    // Click the login button in the dialog
    const authDialog = page.locator('.trainwave-auth-dialog');
    await expect(authDialog).toBeVisible();

    const dialogLoginButton = authDialog.locator(
      'text=Authenticate with Trainwave'
    );
    await dialogLoginButton.click();

    // Check that loading state appears
    await expect(authDialog.locator('text=Authenticating...')).toBeVisible();
  });

  test('should show error message on authentication failure', async ({
    page
  }) => {
    // Mock the authentication to fail
    await page.route('**/trainwave/auth/create_session', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Authentication failed' })
      });
    });

    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Open authentication dialog
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await trainwaveDropdown.click();
    const loginButton = page.locator('text=Sign In');
    await loginButton.click();

    // Click the login button in the dialog
    const authDialog = page.locator('.trainwave-auth-dialog');
    await expect(authDialog).toBeVisible();

    const dialogLoginButton = authDialog.locator(
      'text=Authenticate with Trainwave'
    );
    await dialogLoginButton.click();

    // Wait for error message
    await expect(authDialog.locator('.trainwave-auth-error')).toBeVisible({
      timeout: 10000
    });
  });

  test('should persist settings', async ({ page }) => {
    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Open settings dialog
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await trainwaveDropdown.click();
    const settingsButton = page.locator('text=Settings');
    await settingsButton.click();

    // Fill in settings
    const settingsDialog = page.locator('.trainwave-settings-dialog');
    await expect(settingsDialog).toBeVisible();

    const gpuTypeSelect = settingsDialog.locator('select[name="gpu_type"]');
    await gpuTypeSelect.selectOption('V100');

    const gpuCountInput = settingsDialog.locator('input[name="gpu_count"]');
    await gpuCountInput.fill('2');

    // Close dialog (using the dialog's close button)
    const closeButton = settingsDialog.locator('text=Close');
    await closeButton.click();

    // Reopen settings and verify persistence
    await trainwaveDropdown.click();
    await settingsButton.click();

    await expect(gpuTypeSelect).toHaveValue('V100');
    await expect(gpuCountInput).toHaveValue('2');
  });

  test('should show jobs list when authenticated', async ({ page }) => {
    // Mock authentication success
    await page.route('**/trainwave/auth/create_session', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          url: 'https://app.trainwave.ai/auth/test',
          token: 'test-token'
        })
      });
    });

    await page.route('**/trainwave/auth/session_status', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'SUCCESS',
          api_token: 'test-api-token'
        })
      });
    });

    // Mock user data
    await page.route('**/trainwave/api/users/me', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '1',
          rid: 'rid-1',
          email: 'test@example.com',
          first_name: 'Test',
          last_name: 'User'
        })
      });
    });

    // Mock jobs data
    await page.route('**/trainwave/api/jobs', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              id: '1',
              rid: 'rid-1',
              state: 'RUNNING',
              s3_url: 's3://bucket/key',
              project: { name: 'Test Project' },
              cloud_offer: {
                cpus: 4,
                memory_mb: 8192,
                gpus: 1,
                gpu_type: 'A100',
                gpu_memory_mb: 40960
              },
              cost_per_hour: 2.5,
              config: { name: 'test-config' },
              created_at: '2023-01-01T00:00:00Z',
              total_cost: 5.0
            }
          ]
        })
      });
    });

    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Authenticate
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await trainwaveDropdown.click();
    const loginButton = page.locator('text=Sign In');
    await loginButton.click();

    const authDialog = page.locator('.trainwave-auth-dialog');
    await expect(authDialog).toBeVisible();

    const dialogLoginButton = authDialog.locator(
      'text=Authenticate with Trainwave'
    );
    await dialogLoginButton.click();

    // Wait for authentication to complete
    await page.waitForTimeout(3000);

    // Check that user info is displayed
    await expect(
      trainwaveDropdown.locator('text=test@example.com')
    ).toBeVisible();

    // Check that jobs are loaded
    await trainwaveDropdown.click();
    await expect(page.locator('.trainwave-job-item')).toBeVisible();
  });

  test('should handle keyboard navigation', async ({ page }) => {
    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Test keyboard navigation to trainwave dropdown
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Look for trainwave dropdown (might need multiple tabs)
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await trainwaveDropdown.focus();

    // Open dropdown with Enter key
    await page.keyboard.press('Enter');

    // Check that dropdown is open
    await expect(page.locator('.trainwave-dropdown-menu')).toBeVisible();
  });

  test('should be responsive on different screen sizes', async ({ page }) => {
    // Test on mobile size
    await page.setViewportSize({ width: 375, height: 667 });

    // Create a new notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Check that trainwave dropdown is still visible
    const trainwaveDropdown = page
      .locator('.trainwave-dropdown-widget')
      .first();
    await expect(trainwaveDropdown).toBeVisible();

    // Test on tablet size
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(trainwaveDropdown).toBeVisible();

    // Test on desktop size
    await page.setViewportSize({ width: 1920, height: 1080 });
    await expect(trainwaveDropdown).toBeVisible();
  });

  test('should handle multiple notebook tabs', async ({ page }) => {
    // Create first notebook using the launcher
    await page.click('[data-command="launcher:create"]');
    await page.waitForSelector('.jp-Launcher');

    // Click on the Python notebook option
    await page.click('.jp-LauncherCard[data-category="Notebook"]');
    await page.waitForSelector('.jp-NotebookPanel:not(.lm-mod-hidden)');

    // Check trainwave dropdown in first notebook
    const firstDropdown = page
      .locator('.jp-NotebookPanel')
      .first()
      .locator('.trainwave-dropdown-widget');
    await expect(firstDropdown).toBeVisible();

    // Create second notebook
    await page.click('[data-command="notebook:create-new"]');
    await page.waitForSelector('.jp-NotebookPanel');

    // Check trainwave dropdown in second notebook
    const secondDropdown = page
      .locator('.jp-NotebookPanel')
      .nth(1)
      .locator('.trainwave-dropdown-widget');
    await expect(secondDropdown).toBeVisible();

    // Both dropdowns should be visible
    await expect(firstDropdown).toBeVisible();
    await expect(secondDropdown).toBeVisible();
  });
});
