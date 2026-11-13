import { defineConfig, devices } from '@playwright/test';

const base = process.env.SITE_BASE_PATH ?? '/osint-rondonia';
const origin = 'http://127.0.0.1:4173';

export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  use: { ...devices['Desktop Chrome'], baseURL: origin + base + '/' },
  webServer: { command: 'node tests/serve.mjs', url: origin + base + '/' },
});
