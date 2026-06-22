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
  timeout: 180_000,
  use: {
    baseURL: 'https://www.jumia.com.ng',
    locale: 'en-NG',
    timezoneId: 'Africa/Lagos',
    trace: 'on-first-retry',
    screenshot: 'on',
    video: 'on',
    actionTimeout: 20_000,
    navigationTimeout: 90_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  outputDir: 'output/playwright/test-results',
});
