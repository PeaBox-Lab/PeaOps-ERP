import { test, expect, type Page } from '@playwright/test';

const BASE = process.env.E2E_BASE_URL ?? 'http://localhost:8080';

async function signIn(page: Page) {
  await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded' });
  await expect(page.locator('text=Welcome back')).toBeVisible();
  await page.fill('input[placeholder="admin"]', 'admin');
  await page.fill('input[placeholder="••••••••••••"]', 'Admin@123456');
  await page.click('button:has-text("Sign in")');
  await expect(page.locator('text=COMMAND CENTER')).toBeVisible({ timeout: 15_000 });
}

test.beforeEach(async ({ page }) => { await signIn(page); });

test('invoice detail shows totals', async ({ page }) => {
  await page.goto(`${BASE}/#/finance/invoices`, { waitUntil: 'domcontentloaded' });
  await expect(page.locator('table')).toBeVisible({ timeout: 10_000 });
  await expect(page.locator('text=INV00001')).toBeVisible();
});

test('search finds invoice', async ({ page }) => {
  await page.goto(`${BASE}/#/search/INV`, { waitUntil: 'domcontentloaded' });
  await expect(page.locator('table')).toBeVisible({ timeout: 10_000 });
});

test('print button renders', async ({ page }) => {
  await page.goto(`${BASE}/#/finance/invoices`, { waitUntil: 'domcontentloaded' });
  await expect(page.locator('button:has-text("Print")')).toBeVisible();
});