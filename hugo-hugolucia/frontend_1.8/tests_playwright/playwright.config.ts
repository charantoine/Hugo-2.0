import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig, devices } from '@playwright/test'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const frontendRoot = path.join(__dirname, '..')
const baseURL = process.env.SMOKE_BASE_URL || 'http://localhost:5173'

export default defineConfig({
  testDir: '.',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list']],
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev -- --port 5173 --strictPort',
    cwd: frontendRoot,
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    env: {
      ...process.env,
      // Override .env.development (Encoors) — smoke tests target local backend via Vite proxy.
      VITE_API_URL: '/api',
    },
  },
})
