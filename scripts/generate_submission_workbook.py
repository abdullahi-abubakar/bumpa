#!/usr/bin/env python3
"""Generate Bumpa QA assessment submission workbook."""

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUTPUT = "/Users/mac/Projects/Bumpa/output/Bumpa_Jumia_QA_Assessment.xlsx"

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(bold=True, size=14, color="1F4E79")
SUBTITLE_FONT = Font(bold=True, size=11)
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Side(style="thin", color="CCCCCC")


def border():
    return Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def style_header_row(ws, row, col_count):
    for col in range(1, col_count + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = border()


def write_table(ws, start_row, headers, rows, widths=None):
    for c, h in enumerate(headers, 1):
        ws.cell(row=start_row, column=c, value=h)
    style_header_row(ws, start_row, len(headers))
    r = start_row + 1
    for row in rows:
        for c, val in enumerate(row, 1):
            cell = ws.cell(row=r, column=c, value=val)
            cell.alignment = WRAP
            cell.border = border()
        r += 1
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
    return r


def add_title_block(ws, title, lines):
    ws["A1"] = title
    ws["A1"].font = TITLE_FONT
    row = 2
    for line in lines:
        ws.cell(row=row, column=1, value=line).alignment = WRAP
        row += 1
    return row + 1


def build_workbook():
    wb = Workbook()

    # --- Sheet 1: Summary ---
    ws = wb.active
    ws.title = "Summary"
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 80
    summary_rows = [
        ("Assessment", "Bumpa QA Recruitment - Jumia Nigeria E2E Flow"),
        ("Target URL", "https://www.jumia.com.ng/"),
        ("Scenario", "Sign up, search Nivea Body Lotion and Oraimo Powerbank, filter results, add to cart across two sellers, attempt checkout, abandon before payment"),
        ("Date Completed", "20 June 2026"),
        ("Framework", "Playwright + POM + Gherkin (happy path)"),
        ("Products Tested", "NIVEA Nourishing Cocoa Body Lotion 400ml (Pack of 2) - Official Store - NGN 6,305 | Oraimo Traveler 15 Power Bank 20000mAh - Third-party seller (90% score) - NGN 14,501"),
        ("Cart Total at Abandonment", "NGN 20,806 (2 items)"),
        ("Checkout Outcome", "Redirected to login/identification gate. No payment made."),
        ("Bugs Found", "5 issues documented (1 Medium, 1 High-for-automation, 1 Info, 2 Low)"),
        ("Submission Email", "people@getbumpa.com"),
        ("Evidence", "output/playwright/cart-two-sellers.png, checkout-login-gate.png, Playwright HTML report"),
        ("Repo Artifacts", "docs/BUMPA_QA_ASSESSMENT.md, features/multi-seller-checkout.feature, lib/pages/, tests/jumia-checkout-flow.spec.ts"),
    ]
    ws["A1"] = "Bumpa QA Assessment - Executive Summary"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:B1")
    r = 3
    for k, v in summary_rows:
        ws.cell(row=r, column=1, value=k).font = SUBTITLE_FONT
        ws.cell(row=r, column=1).alignment = WRAP
        ws.cell(row=r, column=2, value=v).alignment = WRAP
        r += 1

    # --- Sheet 2: Test Plan ---
    ws2 = wb.create_sheet("Test Plan")
    r = add_title_block(
        ws2,
        "Test Plan: Onboarding + First-Time Checkout",
        [
            "Objective: Validate a new user can sign up, search, filter, build a multi-seller cart, and reach checkout without completing payment.",
            "Approach: Combined manual exploratory testing and Playwright E2E automation with evidence capture.",
        ],
    )
    write_table(
        ws2,
        r,
        ["Category", "Details"],
        [
            ["In Scope", "Sign-up/sign-in initiation; product search; catalogue filters; add-to-cart (multi-seller); cart summary; checkout entry; abandon before payment"],
            ["Out of Scope", "Payment completion; post-order tracking; returns/refunds; mobile native app; load/performance benchmarking"],
            ["Entry Criteria", "Access to jumia.com.ng; Chromium browser; Playwright installed; test email for sign-up attempt"],
            ["Exit Criteria", "All P1 test cases executed; bugs logged; checkout abandoned before payment; automation suite committed"],
            ["Test Environment", "Production - https://www.jumia.com.ng/ - Desktop Chrome - macOS"],
        ],
        [22, 90],
    )

    # --- Sheet 3: Test Cases ---
    ws3 = wb.create_sheet("Test Cases")
    cases = [
        ("TC-01", "Homepage load", "Navigate to jumia.com.ng", "Page loads; cookie consent shown", "P1", "Manual + Auto", "Pass"),
        ("TC-02", "Cookie consent", "Accept or reject optional cookies", "Overlay dismissed; site usable", "P1", "Auto helper", "Pass with workaround"),
        ("TC-03", "Sign-up initiation", "Account > Sign In > enter email > Continue", "Redirect to OTP verification screen", "P1", "Partial auto", "Pass"),
        ("TC-04", "OTP verification", "Enter code from email", "Account created / logged in", "P1", "Manual only", "Blocked - needs mailbox"),
        ("TC-05", "Search Nivea Body Lotion", "Search Nivea Body Lotion", "Catalog results with relevant products", "P1", "Automated", "Pass"),
        ("TC-06", "Filter Express Delivery", "Click Jumia Express filter", "URL updates; results filtered", "P2", "Automated", "Pass"),
        ("TC-07", "Filter Oraimo brand", "Search Oraimo > Brand filter", "Oraimo-only results", "P2", "Automated", "Pass"),
        ("TC-08", "PDP Nivea Official Store", "Open product; verify seller badge", "Official Store badge visible", "P1", "Automated", "Pass"),
        ("TC-09", "Add Nivea to cart", "Click Add to cart", "Cart count increments", "P1", "Automated", "Pass"),
        ("TC-10", "PDP Oraimo third-party", "Open product; verify seller score", "Non-Official seller shown (90% score)", "P1", "Automated", "Pass"),
        ("TC-11", "Add Oraimo to cart", "Click Add to cart", "Cart shows 2 items", "P1", "Automated", "Pass"),
        ("TC-12", "Cart summary", "Open /cart/", "Both items; subtotal NGN 20,806", "P1", "Automated", "Pass"),
        ("TC-13", "Checkout initiation", "Click Checkout (NGN 20,806)", "Redirect to login/identification", "P1", "Automated", "Pass"),
        ("TC-14", "Abandon before payment", "Stop at login gate", "No payment processed", "P1", "Manual abort", "Pass"),
    ]
    write_table(
        ws3,
        1,
        ["ID", "Test Case", "Steps", "Expected Result", "Priority", "Automation", "Status"],
        cases,
        [10, 24, 40, 36, 10, 14, 12],
    )

    # --- Sheet 4: Tools & Duration ---
    ws4 = wb.create_sheet("Tools & Duration")
    write_table(
        ws4,
        1,
        ["Tool", "Purpose"],
        [
            ("Playwright (@playwright/test)", "E2E automation, CI-ready test suite"),
            ("Playwright CLI", "Interactive exploratory testing, screenshots, snapshots"),
            ("Chromium (Desktop Chrome)", "Primary test browser"),
            ("Browser DevTools / Console", "JavaScript error detection"),
            ("Screenshots and video", "Evidence capture on failure"),
            ("GitHub Actions", "CI pipeline on push/PR and weekly smoke"),
            ("HTML Reporter", "Test run reporting (npm run report)"),
            ("Page Object Model (lib/pages/)", "Maintainable selector layer"),
            ("Gherkin feature file", "Stakeholder-readable happy-path scenario"),
        ],
        [32, 70],
    )
    write_table(
        ws4,
        13,
        ["Activity", "Estimated Duration"],
        [
            ("Manual exploratory run (first pass)", "45-60 minutes"),
            ("Playwright setup and test authoring", "60-90 minutes"),
            ("Automated regression run", "30 seconds (1 test) / ~3 min (full suite)"),
            ("Bug documentation and report", "30-45 minutes"),
            ("TOTAL first-time completion", "3-4 hours"),
            ("Repeat regression (automated)", "Under 5 minutes"),
        ],
        [40, 30],
    )

    # --- Sheet 5: Automation Strategy ---
    ws5 = wb.create_sheet("Automation Strategy")
    write_table(
        ws5,
        1,
        ["Question", "Answer"],
        [
            (
                "What would you automate first and why?",
                "POM-based domain objects first (lib/pages/ + lib/jumia-flow.ts), then BDD/Gherkin only for core happy-path scenarios stakeholders care about (multi-seller checkout). Automate TC-05 through TC-12 first: search, filter, add-to-cart, cart validation. Highest value, most repeatable, lowest flake without OTP.",
            ),
            (
                "Priority order",
                "1st: POM pages + CheckoutFlow domain object | 2nd: Happy-path Gherkin (features/multi-seller-checkout.feature) | 3rd: Plain Playwright specs for negative/edge cases | 4th: OTP/auth once test-mailbox is wired",
            ),
            (
                "Why not Gherkin for everything?",
                "Gherkin adds overhead without clarity for low-level negatives (cookie modal interception, Cloudflare stalls, OTP timeouts). Keep those in technical specs for easier debugging.",
            ),
            (
                "Architecture",
                "features/*.feature -> lib/jumia-flow.ts -> lib/pages/*.page.ts -> tests/*.spec.ts (test.step maps to Gherkin)",
            ),
        ],
        [28, 95],
    )
    write_table(
        ws5,
        8,
        ["Automate First (Priority)", "Test Cases", "Rationale"],
        [
            ("1st", "TC-05, TC-08-TC-12", "Core revenue path; stable DOM; no OTP dependency"),
            ("2nd", "TC-06, TC-07", "Filter URL assertions are reliable regression checks"),
            ("3rd", "TC-13", "Checkout redirect without payment"),
            ("4th", "TC-01, TC-02", "Prerequisite helpers in beforeEach hooks"),
        ],
        [22, 22, 60],
    )

    # --- Sheet 6: Manual Testing ---
    ws6 = wb.create_sheet("Manual Only")
    write_table(
        ws6,
        1,
        ["Area", "Reason", "Related TC"],
        [
            ("OTP / email verification", "Requires real mailbox or test inbox API (Mailosaur, MailSlurp)", "TC-04"),
            ("Payment flows", "Assessment forbids payment; PCI compliance scope", "N/A"),
            ("Cloudflare bot challenges", "Non-deterministic in CI; needs staging bypass", "TC-13"),
            ("Visual / UX review", "Promo banners, responsive layout, accessibility", "TC-01"),
            ("Cross-browser matrix", "Safari/Firefox payment and auth quirks", "All"),
            ("Social login (Google/Facebook/Apple)", "OAuth popups; third-party dependency", "TC-03"),
            ("Seller disputes / post-checkout", "Outside core checkout funnel", "N/A"),
        ],
        [30, 55, 15],
    )

    # --- Sheet 7: CI Integration ---
    ws7 = wb.create_sheet("CI Integration")
    write_table(
        ws7,
        1,
        ["Component", "Details"],
        [
            ("Framework", "Playwright Test + POM + Gherkin (happy path only)"),
            ("Trigger", "Push/PR to main; weekly smoke (Monday 06:00 UTC)"),
            ("Pipeline", "GitHub Actions -> npm ci -> playwright install chromium -> npx playwright test -> upload HTML report artifact"),
            ("Config file", "playwright.config.ts"),
            ("Workflow file", ".github/workflows/playwright.yml"),
            ("Test spec", "tests/jumia-checkout-flow.spec.ts"),
            ("Feature file", "features/multi-seller-checkout.feature"),
            ("Artifacts retained", "14 days - HTML report, screenshots, video on failure"),
            ("Recommended hardening", "Mailosaur secret for OTP; storageState for auth; staging env without Cloudflare"),
        ],
        [24, 85],
    )

    # --- Sheet 8: Bugs ---
    ws8 = wb.create_sheet("Bugs Found")
    bugs = [
        (
            "BUG-001",
            "Medium",
            "Cookie consent blocks critical interactions",
            "Cookie modal intercepts pointer events on Account, Search, Add to cart until dismissed. Reappears on new sessions.",
            "1. Open jumia.com.ng (fresh session)\n2. Click Account or Search without accepting cookies",
            "Primary navigation usable with non-blocking consent",
            "Click timeout - modal intercepts events",
            "TC-02",
            "Playwright traces; manual repro",
        ),
        (
            "BUG-002",
            "Low",
            "Recurring JS TypeError on product/cart pages",
            "Console: TypeError: Cannot read properties of undefined (reading 'initialised'). Likely analytics/tracking script failure.",
            "Open any product or cart page; inspect console",
            "No console errors from core scripts",
            "Repeated TypeError in console",
            "TC-08-TC-12",
            "Console logs in .playwright-cli/",
        ),
        (
            "BUG-003",
            "High (automation)",
            "Cloudflare challenge blocks checkout/login",
            "Navigating to /customer/account/login/?return=checkout triggers 'Performing security verification' page. Automated browsers stall or fail.",
            "1. Add items to cart\n2. Click Checkout",
            "Smooth redirect to login within seconds",
            "Cloudflare challenge; 15-60s+ delay or timeout",
            "TC-13",
            "checkout-login-gate.png; Ray ID in page",
        ),
        (
            "BUG-004",
            "Info / Design",
            "Guest checkout requires authentication",
            "Checkout redirects to login. No guest checkout path observed.",
            "1. Add items as guest\n2. Click Checkout",
            "Optional guest checkout (common e-commerce pattern)",
            "Login required before checkout summary",
            "TC-13",
            "May be intentional product decision",
        ),
        (
            "BUG-005",
            "Low",
            "Search relevance - wrong product category",
            "Searching 'Nivea Body Lotion' surfaces anti-perspirant/deodorant in sponsored slots before body lotions.",
            "1. Search 'Nivea Body Lotion'\n2. Review top results",
            "Body lotion products ranked first",
            "Deodorant/anti-perspirant in top slots",
            "TC-05",
            "Search results screenshot",
        ),
    ]
    write_table(
        ws8,
        1,
        ["ID", "Severity", "Title", "Description", "Steps to Reproduce", "Expected", "Actual", "Test Case", "Evidence"],
        bugs,
        [10, 14, 28, 40, 36, 28, 28, 10, 24],
    )

    # --- Sheet 9: Bug Reporting ---
    ws9 = wb.create_sheet("Bug Reporting")
    write_table(
        ws9,
        1,
        ["Step", "Action"],
        [
            ("1. Log ticket", "Create Jira/Linear issue with BUG-ID, severity, environment, linked TC-ID"),
            ("2. Attach evidence", "Screenshot, video, Playwright trace, console snippet, exact URL"),
            ("3. Write repro steps", "Numbered steps any engineer can follow without QA context"),
            ("4. Tag owners", "Tag @engineering for P1/P2; include Cloudflare Ray ID when applicable"),
            ("5. Fast triage", "Share summary in Slack/Teams with severity and user impact"),
            ("6. Archive", "Store full report in Confluence/Notion; link CI artifact"),
        ],
        [18, 85],
    )
    write_table(
        ws9,
        10,
        ["Channel", "When to Use"],
        [
            ("Jira / Linear", "Primary defect tracking and traceability"),
            ("Slack / Teams", "Fast triage and severity escalation"),
            ("GitHub Issues", "If engineering uses GitHub; attach Playwright trace"),
            ("Confluence / Notion", "Test report archive and release notes"),
        ],
        [20, 70],
    )

    # --- Sheet 10: Traceability ---
    ws10 = wb.create_sheet("Traceability")
    write_table(
        ws10,
        1,
        ["Requirement", "Test Case", "Automation", "Status"],
        [
            ("User can sign up", "TC-03, TC-04", "Partial - stops at OTP", "Blocked at OTP"),
            ("Search products", "TC-05", "Automated", "Pass"),
            ("Filter results", "TC-06, TC-07", "Automated", "Pass"),
            ("Add from 2 sellers", "TC-09-TC-11", "Automated", "Pass"),
            ("View cart", "TC-12", "Automated", "Pass"),
            ("Reach checkout", "TC-13", "Automated", "Pass"),
            ("No payment made", "TC-14", "Manual abort", "Pass"),
        ],
        [28, 16, 22, 16],
    )
    write_table(
        ws10,
        11,
        ["Traceability Practice", "Implementation"],
        [
            ("Test Case IDs", "TC-01 to TC-14 map to specs and manual charters"),
            ("Playwright annotations", "Document abandonment points in test.info()"),
            ("Git commits", "Link automation code to assessment deliverable"),
            ("CI artifacts", "HTML report, screenshots, video retained 14 days"),
            ("Defect linking", "BUG-XXX references TC-XX in ticket system"),
        ],
        [28, 70],
    )

    # --- Sheet 11: Risks ---
    ws11 = wb.create_sheet("Risk Mitigation")
    write_table(
        ws11,
        1,
        ["Risk", "Likelihood", "Impact", "Mitigation"],
        [
            ("Cloudflare blocks CI", "High", "High", "storageState; off-peak runs; staging bypass"),
            ("OTP/email dependency", "High", "Medium", "Mailosaur integration; mock auth in staging"),
            ("Cookie modal flakiness", "Medium", "Medium", "dismissOverlays() helper in beforeEach"),
            ("Product URLs change", "Medium", "Low", "Parameterize slugs; search-then-pick pattern"),
            ("Price/stock drift", "Medium", "Low", "Assert structure not exact price"),
            ("Multi-seller shipping split", "Low", "Medium", "Manual test delivery fees at checkout"),
            ("Accidental payment", "Low", "Critical", "Abort at login gate; never store card data"),
        ],
        [30, 12, 12, 55],
    )

    # --- Sheet 12: Recommendations ---
    ws12 = wb.create_sheet("Recommendations")
    write_table(
        ws12,
        1,
        ["Audience", "Recommendation", "Rationale"],
        [
            ("Product", "Offer guest checkout", "Reduces friction; users abandon at login wall"),
            ("Product", "Improve search relevance for body lotion queries", "Deodorant surfaced before lotions confuses shoppers"),
            ("Product", "Show per-seller shipping in cart before checkout", "Multi-seller carts need delivery clarity"),
            ("Product", "Extend onboarding progress through first purchase", "Sign-up has progress bar; checkout does not"),
            ("Product", "Non-blocking cookie banner for essential actions", "Modal blocks Account, Search, Add to cart"),
            ("Engineering", "Fix 'initialised' TypeError in tracking scripts", "Silent analytics failure on product/cart pages"),
            ("Engineering", "Add data-testid on Account, Search, Add to cart, Checkout", "Stabilises automation selectors"),
            ("Engineering", "Provide staging/UAT without Cloudflare", "Unblocks CI and OTP testing"),
            ("Engineering", "API-level cart/session test hooks", "Faster integration tests beneath E2E"),
            ("Engineering", "Accessibility audit on account menu checkbox pattern", "Keyboard/screen-reader flow unclear"),
            ("QA", "Integrate Mailosaur for OTP in CI", "Completes sign-up automation path"),
            ("QA", "Split suite: smoke vs auth vs checkout", "Faster feedback on core path"),
            ("QA", "Visual regression on PDP and cart", "Catch layout regressions early"),
            ("QA", "Quarterly Firefox + WebKit runs", "Cross-browser payment/auth coverage"),
        ],
        [14, 55, 45],
    )

    wb.save(OUTPUT)
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    build_workbook()
