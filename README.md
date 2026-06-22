# Bumpa — Jumia QA Assessment

Playwright E2E test project for the Bumpa recruitment QA assessment (Jumia Nigeria checkout flow).

## Quick start

```bash
npm install
npx playwright install chromium
npm test
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm test` | Run E2E tests headless |
| `npm run test:headed` | Run with visible browser |
| `npm run test:evidence` | Run test + copy video to `output/playwright/checkout-flow.webm` |
| `npm run test:ui` | Playwright UI mode |
| `npm run report` | Open HTML test report |

## Scenario covered

1. Search **Nivea Body Lotion** via header → open first result → add to cart
2. Search **Oraimo Powerbank** via header → open first non-Official Store result → add to cart
3. Click **Cart** → **Checkout** → abandon at login gate (no payment)

## Evidence

After `npm run test:evidence`:

- `output/playwright/checkout-flow.webm` — full run video
- `output/playwright/cart-two-sellers.png` — cart screenshot
- `output/playwright/checkout-login-gate.png` — checkout/login gate screenshot

## Submission

Primary deliverable: `docs/Bumpa_Jumia_QA_Assessment.docx`

Local submission checklist: `docs/SUBMISSION_README.txt` (gitignored)

Regenerate: `python3 scripts/generate_submission_docx.py`
