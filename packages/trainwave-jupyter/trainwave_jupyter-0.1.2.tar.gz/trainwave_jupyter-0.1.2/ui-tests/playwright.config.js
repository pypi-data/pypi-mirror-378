/**
 * Configuration for Playwright using default from @jupyterlab/galata
 */
const baseConfig = require('@jupyterlab/galata/lib/playwright-config');

// Use JUPYTER_URL from environment if available, otherwise default
const jupyterUrl = process.env.JUPYTER_URL || 'http://localhost:8888/lab';

module.exports = {
    ...baseConfig,
    testDir: './tests',
    testMatch: '**/*.spec.ts',
    webServer: process.env.JUPYTER_URL ? undefined : {
        command: 'jlpm start',
        url: jupyterUrl,
        timeout: 120 * 1000,
        reuseExistingServer: !process.env.CI
    },
    use: {
        baseURL: jupyterUrl,
    }
};