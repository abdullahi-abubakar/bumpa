# Bumpa QA Assessment — Jumia Nigeria E2E Flow

**Candidate:** QA Assessment Submission  
**Target:** [Jumia Nigeria](https://www.jumia.com.ng/)  
**Scenario:** New user sign-up → search → filter → multi-seller cart → checkout (abandon before payment)  
**Date:** 20 June 2026  
**Automation:** Playwright (`@playwright/test` v1.61)

---

## Executive Summary

I executed the full onboarding + first-time checkout scenario on Jumia Nigeria using manual exploratory testing and Playwright automation. The shopping path (search, filter, add-to-cart across two sellers, cart review, checkout initiation) works for guest users up to the authentication gate. Sign-up requires email OTP verification, and checkout requires login — both block full unattended automation without test-mailbox or auth bypass tooling.

**Products tested:**
| Product | Seller | Price | Filter applied |
|---------|--------|-------|----------------|
| NIVEA Nourishing Cocoa Body Lotion 400ml (Pack of 2) | Official Store (100% Seller Score) | ₦6,305 | Express Delivery |
| Oraimo Traveler 15 Power Bank 20000mAh | Third-party seller (90% Seller Score) | ₦14,501 | Oraimo brand filter |

**Cart total at abandonment:** ₦20,806 (2 items)

---

## 1. Test Plan

### 1.1 Scope

| In scope | Out of scope |
|----------|--------------|
| Account sign-up / sign-in initiation | Completing payment |
| Product search & catalogue filters | Post-order tracking |
| Add-to-cart (multi-seller) | Returns/refunds |
| Cart summary validation | Mobile native app |
| Checkout entry & auth gate | Load/performance benchmarking |

### 1.2 Test Cases

| ID | Test Case | Steps | Expected Result | Priority |
|----|-----------|-------|-----------------|----------|
| TC-01 | Homepage load | Navigate to jumia.com.ng | Page loads; cookie consent shown | P1 |
| TC-02 | Cookie consent | Accept / reject optional cookies | Overlay dismissed; site usable | P1 |
| TC-03 | Sign-up initiation | Account → Sign In → enter email → Continue | Redirect to OTP verification screen | P1 |
| TC-04 | OTP verification | Enter code from email | Account created / logged in | P1 |
| TC-05 | Search — Nivea Body Lotion | Search bar → "Nivea Body Lotion" → Enter | Catalog results with relevant products | P1 |
| TC-06 | Filter — Express Delivery | Click Jumia Express filter | URL updates; results filtered | P2 |
| TC-07 | Filter — Brand (Oraimo) | Search Oraimo → Brand filter | Oraimo-only results | P2 |
| TC-08 | PDP — Nivea (Official Store) | Open product → verify seller badge | Official Store badge visible | P1 |
| TC-09 | Add Nivea to cart | Click Add to cart | Confirmation + cart count increments | P1 |
| TC-10 | PDP — Oraimo (3rd-party seller) | Open product → verify seller score | Non-Official seller shown | P1 |
| TC-11 | Add Oraimo to cart | Click Add to cart | Cart shows 2 items | P1 |
| TC-12 | Cart summary | Open /cart/ | Both items, correct prices, subtotal ₦20,806 | P1 |
| TC-13 | Checkout initiation | Click "Checkout (₦20,806)" | Redirect to login/identification | P1 |
| TC-14 | Abandon before payment | Stop at login/OTP — do not pay | No payment processed | P1 |

### 1.3 Tools Used

| Tool | Purpose |
|------|---------|
| **Playwright** (`@playwright/test`) | E2E automation, CI-ready test suite |
| **Playwright CLI** | Interactive exploratory testing, screenshots, snapshots |
| **Chromium** | Primary browser (Desktop Chrome profile) |
| **Browser DevTools / Console** | JS error detection |
| **Screenshots & video** | Evidence capture on failure |
| **GitHub Actions** | CI pipeline (workflow included in repo) |
| **HTML Reporter** | Test run reporting (`npm run report`) |

### 1.4 Estimated Duration

| Activity | Time |
|----------|------|
| Manual exploratory run (first pass) | 45–60 min |
| Playwright setup + test authoring | 60–90 min |
| Automated regression run | ~30 sec (1 test) / ~3 min (full suite) |
| Bug documentation & report | 30–45 min |
| **Total first-time completion** | **~3–4 hours** |
| **Repeat regression (automated)** | **< 5 minutes** |

---

## 2. Automation Strategy

### 2.1 What I Would Automate First (and Why)

**Short answer:** Build **POM-based domain objects first**, then layer **BDD/Gherkin on top only for core happy-path scenarios** that matter to stakeholders — like this exact multi-seller checkout flow. Do **not** write Gherkin for every edge case; low-level negative tests (cookie-modal interception, Cloudflare stalls, OTP timeouts) belong in plain Playwright specs where they are cheaper to maintain and easier to debug.

#### Layer 1 — Page Object Model (foundation)

| Page object | Responsibility |
|-------------|----------------|
| `HomePage` | Landing, overlay dismissal, account menu |
| `AuthPage` | Sign-in / sign-up, OTP screen detection |
| `CatalogPage` | Search, filters (Express, brand) |
| `ProductPage` | PDP validation, add-to-cart |
| `CartPage` | Multi-item cart, checkout entry |
| `CheckoutFlow` | Composes pages into business actions |

**Automate first at this layer:** TC-05 → TC-12 (search → filter → add-to-cart → cart). These are the highest-value, most-repeatable paths. Selectors live in one place; UI changes require one fix, not scattered spec updates.

#### Layer 2 — BDD/Gherkin (stakeholder happy paths only)

| Write Gherkin for | Do NOT write Gherkin for |
|-------------------|--------------------------|
| Multi-seller checkout happy path (`features/multi-seller-checkout.feature`) | Cookie-consent click interception |
| First-time sign-up → cart → checkout abandon | Cloudflare challenge behaviour |
| Core smoke scenarios product/PM care about | OTP negative cases, payment edge cases |
| | Seller-score boundary values, filter permutations |

**Why:** Gherkin earns its overhead when PMs, QA leads, and engineers need a **shared readable contract** for a critical journey. Writing `Given the cookie modal intercepts pointer events` adds ceremony without clarity — those belong in technical specs with `test.describe('cookie overlay')`.

#### Priority order

| Priority | What | Layer |
|----------|------|-------|
| **1st** | POM pages + `CheckoutFlow` domain object | POM |
| **2nd** | Happy-path Gherkin for this checkout scenario | BDD |
| **3rd** | Plain Playwright specs for negative/edge cases | Specs only |
| **4th** | OTP/auth completion once test-mailbox is wired | POM + secret in CI |

```
features/multi-seller-checkout.feature   ← stakeholders read this
        ↓
lib/jumia-flow.ts                      ← domain actions
        ↓
lib/pages/*.page.ts                    ← selectors & interactions
        ↓
tests/jumia-checkout-flow.spec.ts      ← test.step() maps to Gherkin
```

### 2.2 Manual Testing Only

| Area | Reason |
|------|--------|
| **OTP / email verification (TC-04)** | Requires real mailbox or test inbox API (Mailosaur, MailSlurp) |
| **Payment flows** | Assessment explicitly forbids payment; PCI scope |
| **Cloudflare bot challenges** | Non-deterministic in CI; needs stealth config or staging bypass |
| **Visual/UX review** | Promo banners, responsive layout, accessibility |
| **Cross-browser matrix** | Safari/Firefox payment quirks — periodic manual sweep |
| **Social login (Google/Facebook/Apple)** | OAuth popups; third-party dependency |
| **Seller communication / disputes** | Outside core checkout funnel |

### 2.3 CI Integration

```
Push/PR → GitHub Actions → npm ci → playwright install → npx playwright test → upload HTML report artifact
```

**Framework:** Playwright Test + POM + Gherkin (happy path)  
**Config:** `playwright.config.ts`  
**Feature:** `features/multi-seller-checkout.feature`  
**Flow:** `lib/jumia-flow.ts`  
**Test:** `tests/jumia-checkout-flow.spec.ts`  
**Schedule:** Weekly smoke (Monday 06:00 UTC) + on every PR

**Run locally:**
```bash
npm install
npx playwright install chromium
npm test                  # headless
npm run test:headed       # visible browser
npm run report            # open HTML report
```

**Recommended CI hardening:**
- Store `JUMIA_TEST_EMAIL` + Mailosaur API key as GitHub secrets for OTP flows
- Add `storageState` fixture to reuse authenticated sessions
- Run against staging/UAT if available to avoid Cloudflare blocks

---

## 3. Bug Reporting

### 3.1 Issues Found During Testing

#### BUG-001 — Cookie consent blocks critical interactions (Severity: Medium)

**Description:** The cookie consent modal intercepts pointer events on Account, Search, and Add to cart buttons until dismissed. Reappears on new sessions/pages.

**Steps to reproduce:**
1. Open jumia.com.ng (fresh session)
2. Click Account or Search without accepting cookies

**Expected:** Primary navigation usable; consent non-blocking for essential actions  
**Actual:** Click timeout — modal intercepts events  
**Evidence:** Playwright traces; manual repro confirmed  
**Environment:** Chrome/macOS, jumia.com.ng  

---

#### BUG-002 — Recurring JS TypeError on product/cart pages (Severity: Low)

**Description:** Console logs repeatedly show:
```
TypeError: Cannot read properties of undefined (reading 'initialised')
```

**Impact:** Unknown user-facing impact; suggests analytics/tracking script failing silently  
**Recommendation:** Engineering to identify failing script bundle  

---

#### BUG-003 — Cloudflare challenge blocks automated checkout/login (Severity: High for automation)

**Description:** Navigating to `/customer/account/login/?return=...checkout...` triggers Cloudflare "Performing security verification" page. Automated browsers may stall 15–60+ seconds or fail.

**Impact:** Blocks unattended E2E in CI; may affect real users on suspicious networks  
**Workaround:** Manual wait; authenticated `storageState`; staging environment without CF  

---

#### BUG-004 — Guest checkout requires authentication (Severity: Info / Design)

**Description:** Clicking Checkout redirects to login rather than guest checkout.

**Expected (per some e-commerce norms):** Optional guest checkout  
**Actual:** Login required before checkout summary  
**Note:** May be intentional for Jumia; document as product decision  

---

#### BUG-005 — Search results include tangentially related products (Severity: Low)

**Description:** Searching "Nivea Body Lotion" returns anti-perspirant/deodorant products in sponsored/top slots before body lotions.

**Impact:** UX confusion; lower search relevance  
**Recommendation:** Tune search ranking / sponsored placement rules  

---

### 3.2 Bug Report Template (for Engineering)

```markdown
## [BUG-XXX] Short title

**Reporter:** QA  
**Date:** YYYY-MM-DD  
**Severity:** Critical / High / Medium / Low  
**Environment:** Production | jumia.com.ng | Chrome 120 | macOS  
**Test Case:** TC-XX  

### Steps to Reproduce
1. ...
2. ...

### Expected Result
...

### Actual Result
...

### Attachments
- Screenshot: output/playwright/cart-two-sellers.png
- Video: output/playwright/test-results/.../video.webm
- Playwright trace: (on retry)

### Notes
...
```

### 3.3 Sharing with Engineers

| Channel | Use |
|---------|-----|
| **Jira / Linear ticket** | Primary tracking; link TC-ID for traceability |
| **Slack / Teams** | Fast triage with screenshot + severity |
| **GitHub Issue** | If engineering uses GitHub; attach Playwright trace |
| **Confluence / Notion** | Test report archive |

**Best practice:** Always attach screenshot/video, console log snippet, exact URL, and reproduction steps. Tag `@engineering` for P1/P2. Include Ray ID when Cloudflare is involved.

---

## 4. Traceability & Risk Mitigation

### 4.1 Traceability Matrix

| Requirement | Test Case | Automation | Status |
|-------------|-----------|------------|--------|
| User can sign up | TC-03, TC-04 | Partial (stops at OTP) | ⚠️ Blocked at OTP |
| Search products | TC-05 | ✅ Automated | Pass |
| Filter results | TC-06, TC-07 | ✅ Automated | Pass |
| Add from 2 sellers | TC-09–TC-11 | ✅ Automated | Pass |
| View cart | TC-12 | ✅ Automated | Pass |
| Reach checkout | TC-13 | ✅ Automated | Pass |
| No payment made | TC-14 | ✅ Manual abort | Pass |

### 4.2 Risk Identification & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cloudflare blocks CI | High | High | Use `storageState`; schedule off-peak; request staging bypass |
| OTP/email dependency | High | Medium | Integrate Mailosaur; mock auth in staging |
| Cookie modal flakiness | Medium | Medium | `dismissOverlays()` helper in `beforeEach` |
| Product URLs change | Medium | Low | Parameterize product slugs; search-then-pick pattern |
| Price/stock drift | Medium | Low | Assert structure not exact price; use regex ranges |
| Multi-seller shipping split | Low | Medium | Manual test delivery fee breakdown at checkout |
| Payment accidental execution | Low | Critical | Abort at login gate; never store real card data |

### 4.3 Ensuring Traceability

1. **Test Case IDs** (TC-01…TC-14) map to automation specs and manual charters  
2. **Playwright annotations** document abandonment points  
3. **Git commit** links test code to assessment deliverable  
4. **CI artifacts** (HTML report, screenshots, video) retained 14 days  
5. **Requirements → Test Case → Bug** chain maintained in ticket system  

---

## 5. Recommendations

### Product Team

1. **Guest checkout option** — Reduce friction for first-time buyers who abandon at login wall  
2. **Search relevance** — Body lotion queries should not surface deodorant in top slots  
3. **Multi-seller cart clarity** — Show per-seller shipping estimates and delivery windows in cart before checkout  
4. **Onboarding progress indicator** — Sign-up flow has a progress bar; extend through first purchase  
5. **Cookie UX** — Allow essential interactions while showing non-blocking cookie banner  

### Engineering

1. **Fix `initialised` TypeError** — Investigate failing analytics/tracking script  
2. **Add `data-testid` attributes** — Stabilise selectors for Account, Search, Add to cart, Checkout  
3. **Staging environment for QA** — Bypass Cloudflare; seed test accounts with known OTP  
4. **API-level test hooks** — Cart/session APIs for faster integration tests beneath E2E  
5. **Accessibility** — Account menu uses checkbox pattern; verify keyboard/screen-reader flow  

### QA / Automation

1. **Mailosaur integration** for OTP completion in CI  
2. **Split test suite** — `@smoke` (cart flow) vs `@auth` (full signup) vs `@checkout`  
3. **Visual regression** — Percy or Playwright snapshots on PDP and cart  
4. **Cross-browser** — Add Firefox + WebKit projects for quarterly runs  

---

## 6. Project Structure

```
Bumpa/
├── .github/workflows/playwright.yml        # CI pipeline
├── docs/BUMPA_QA_ASSESSMENT.md             # This document
├── features/multi-seller-checkout.feature  # BDD happy path (stakeholders)
├── lib/
│   ├── pages/                              # POM — interactions only
│   └── jumia-flow.ts                       # Domain flow object
├── tests/jumia-checkout-flow.spec.ts       # Spec + assertions; maps to Gherkin
├── playwright.config.ts
├── output/playwright/
│   ├── cart-two-sellers.png
│   └── checkout-login-gate.png
└── package.json
```

---

## 7. Submission Checklist

- [x] Test plan created with tools and time estimates  
- [x] Automation strategy documented  
- [x] Playwright project set up and test passing locally  
- [x] Bugs documented with reproduction steps  
- [x] Traceability matrix and risk mitigation  
- [x] Product/engineering recommendations  
- [ ] Email submission to **people@getbumpa.com** (within 3 days of receipt)

---

*Assessment completed using Playwright against https://www.jumia.com.ng/. No payment was made. Order abandoned at login/checkout gate as instructed.*
