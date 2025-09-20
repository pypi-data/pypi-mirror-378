/**
 * Main Playwright configuration that delegates to UI tests
 */
const path = require('path');

module.exports = {
    testDir: './ui-tests/tests',
    testMatch: '**/*.spec.ts',
    use: {
        baseURL: process.env.JUPYTER_URL || 'http://localhost:8888/lab',
    },
    // Don't start webServer - rely on external JupyterLab instance
    // This should be started by run-tests.sh script
    projects: [{
        name: 'chromium',
        use: {...require('@playwright/test').devices['Desktop Chrome'] },
    }, ],
};