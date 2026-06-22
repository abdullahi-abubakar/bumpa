import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [
    ['list'],
    ['html', { outputFolder: 'output/playwright/report' }],
    ['junit', { outputFile: 'output/playwright/junit.xml' }],
    ...(process.env.CI ? [['github'] as const] : []),
  ],
  timeout: 120_000,
  use: {
    baseURL: 'https://www.jumia.com.ng',
    trace: 'on-first-retry',
    screenshot: 'on',
    video: 'on',
    actionTimeout: 15000,
    navigationTimeout: 60000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  outputDir: 'output/playwright/test-results',
});
