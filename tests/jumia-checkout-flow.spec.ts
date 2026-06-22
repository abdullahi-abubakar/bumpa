import { test, expect, type Page } from '@playwright/test';

async function acceptCookies(page: Page) {
  const btn = page.getByRole('button', { name: 'Accept All Cookies' });
  if (await btn.isVisible({ timeout: 3000 }).catch(() => false)) {
    await btn.click();
    await page.waitForTimeout(500);
  }
}

async function topSearch(page: Page, query: string) {
  await acceptCookies(page);
  const box = page.getByRole('textbox', { name: 'Search' });
  await box.click();
  await box.fill(query);
  await box.press('Enter');
  await page.waitForLoadState('load');
  await acceptCookies(page);
}

async function openFirstProduct(page: Page, skipOfficialStore = false) {
  const cards = page.locator('article').filter({ has: page.locator('h3') });
  await cards.first().waitFor({ state: 'visible', timeout: 20000 });

  const total = await cards.count();
  for (let i = 0; i < total; i++) {
    const text = await cards.nth(i).innerText();
    if (skipOfficialStore && text.includes('Official Store')) continue;
    await cards.nth(i).getByRole('link').first().click();
    break;
  }

  await page.waitForLoadState('load');
  await acceptCookies(page);
}

async function expectCartCount(page: Page, count: number) {
  await expect.poll(async () => {
    const cart = page.locator('a[href="/cart/"]').first();
    const text = await cart.innerText().catch(() => '');
    return text.includes(String(count));
  }, { timeout: 20000 }).toBe(true);
}

async function clickAddToCart(page: Page) {
  const btn = page.locator('#add-to-cart').getByRole('button', { name: /^Add to cart$/i });
  await btn.waitFor({ state: 'visible', timeout: 30000 });
  await acceptCookies(page);
  await btn.click();
  await page.waitForTimeout(1500);
}

test.describe('Jumia multi-seller checkout', () => {
  test.setTimeout(180_000);

  test('Nivea + Oraimo via top search, cart, checkout, no payment', async ({ page }) => {
    await test.step('TC-01/TC-02: load homepage and accept cookies', async () => {
      await page.goto('https://www.jumia.com.ng/');
      await acceptCookies(page);
      await expect(page.getByRole('textbox', { name: 'Search' })).toBeVisible();
    });

    await test.step('TC-05/TC-06/TC-07: search Nivea, open product, add to cart', async () => {
      await topSearch(page, 'Nivea Body Lotion');
      await openFirstProduct(page);
      await clickAddToCart(page);
      await expectCartCount(page, 1);
    });

    await test.step('TC-08/TC-09/TC-10: search Oraimo, open third-party seller, add to cart', async () => {
      await topSearch(page, 'Oraimo Powerbank');
      await openFirstProduct(page, true);
      await clickAddToCart(page);
      await expectCartCount(page, 2);
    });

    await test.step('TC-11: open cart and verify both products', async () => {
      await page.getByRole('link', { name: /Cart/i }).click();
      await page.waitForURL(/\/cart\/?/, { timeout: 15000 });
      await acceptCookies(page);
      await expect(page.getByText(/NIVEA/i).first()).toBeVisible();
      await expect(page.getByText(/Oraimo/i).first()).toBeVisible();
      await page.screenshot({ path: 'output/playwright/cart-two-sellers.png', fullPage: true });
    });

    await test.step('TC-12/TC-13: checkout and abandon before payment', async () => {
      await page.getByRole('link', { name: /Checkout/i }).click();
      await page.waitForURL(/checkout|login|customer|identification/, { timeout: 90000 });
      await expect(page).not.toHaveURL(/payment|pay\.jumia/i);
      await page.screenshot({ path: 'output/playwright/checkout-login-gate.png', fullPage: true });
    });
  });
});
