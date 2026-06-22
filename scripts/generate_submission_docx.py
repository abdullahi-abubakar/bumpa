#!/usr/bin/env python3
"""Generate Bumpa QA assessment Word document for submission."""

import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import qn

ROOT = "/Users/mac/Projects/Bumpa"
OUTPUT = os.path.join(ROOT, "docs/Bumpa_Jumia_QA_Assessment.docx")
CART_SHOT = os.path.join(ROOT, "output/playwright/cart-two-sellers.png")
CHECKOUT_SHOT = os.path.join(ROOT, "output/playwright/checkout-login-gate.png")
VIDEO_PATH = "output/playwright/checkout-flow.webm"


def set_cell_shading(cell, hex_color: str):
    from docx.oxml import OxmlElement

    shading = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    shd.set(qn("w:val"), "clear")
    shading.append(shd)


def add_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        set_cell_shading(hdr[i], "1F4E79")
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(10)
    for row_data in rows:
        row = table.add_row().cells
        for i, val in enumerate(row_data):
            row[i].text = str(val)
            for p in row[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10)
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)
    doc.add_paragraph()
    return table


def add_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.color.rgb = RGBColor(31, 78, 121)
    return h


def add_bullets(doc, items):
    for item in items:
        doc.add_paragraph(item, style="List Bullet")


def add_image_if_exists(doc, path, caption, width=5.5):
    if not os.path.isfile(path):
        doc.add_paragraph(f"[{caption} — generate with: npm run test:evidence]")
        return
    doc.add_picture(path, width=Inches(width))
    cap = doc.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in cap.runs:
        r.italic = True
        r.font.size = Pt(9)
    doc.add_paragraph()


def build():
    doc = Document()

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Bumpa QA Assessment")
    run.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = RGBColor(31, 78, 121)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_run = sub.add_run("Jumia Nigeria - Onboarding + First-Time Checkout Flow")
    sub_run.font.size = Pt(14)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(
        "Target: https://www.jumia.com.ng/  |  Date: 20 June 2026  |  Tool: Playwright\n"
    ).font.size = Pt(10)
    doc.add_paragraph()

    add_heading(doc, "Executive Summary", 1)
    doc.add_paragraph(
        "I executed the full onboarding and first-time checkout scenario on Jumia Nigeria using "
        "manual exploratory testing and a Playwright E2E test. The shopping path works end-to-end: "
        "search from the header, open products, add both items to cart from different sellers, "
        "open cart, and initiate checkout. The flow stops at the login/authentication gate — no "
        "payment was made. Sign-up requires email OTP verification, which blocks full unattended "
        "automation without a test mailbox."
    )
    add_table(
        doc,
        ["Product", "Seller", "Price", "How Selected"],
        [
            ["NIVEA Nourishing Cocoa Body Lotion 400ml (Pack of 2)", "Official Store (100% Seller Score)", "NGN 6,305", "Top search result for Nivea Body Lotion"],
            ["Oraimo Traveler 15 Power Bank 20000mAh", "Third-party seller (90% Seller Score)", "NGN 14,501", "First non-Official Store result for Oraimo Powerbank"],
        ],
        [2.2, 1.8, 0.9, 1.1],
    )
    doc.add_paragraph(
        "Cart total at abandonment: NGN 20,806 (2 items). Automated test passes in ~25 seconds."
    )

    add_heading(doc, "1. Test Plan", 1)
    add_heading(doc, "1.1 Scope", 2)
    add_table(
        doc,
        ["In Scope", "Out of Scope"],
        [
            ["Account sign-up / sign-in initiation", "Completing payment"],
            ["Product search via header search bar", "Post-order tracking"],
            ["Add-to-cart (multi-seller)", "Returns / refunds"],
            ["Cart summary validation", "Mobile native app"],
            ["Checkout entry and auth gate", "Load / performance benchmarking"],
        ],
        [3.25, 3.25],
    )

    add_heading(doc, "1.2 Test Cases", 2)
    cases = [
        ("TC-01", "Homepage load", "Navigate to jumia.com.ng", "Page loads; cookie consent shown", "P1", "Pass"),
        ("TC-02", "Cookie consent", "Accept cookies before interactions", "Overlay dismissed; site usable", "P1", "Pass"),
        ("TC-03", "Sign-up initiation", "Account > Sign In > email > Continue", "Redirect to OTP screen", "P1", "Pass (manual)"),
        ("TC-04", "OTP verification", "Enter code from email", "Account created / logged in", "P1", "Blocked - needs mailbox"),
        ("TC-05", "Search Nivea Body Lotion", "Use header search bar", "Catalog results with relevant products", "P1", "Pass"),
        ("TC-06", "Open Nivea PDP", "Click first search result", "Product page loads; Add to cart visible", "P1", "Pass"),
        ("TC-07", "Add Nivea to cart", "Click Add to cart", "Header shows 1 Cart", "P1", "Pass"),
        ("TC-08", "Search Oraimo Powerbank", "Use header search bar again", "Catalog results shown", "P1", "Pass"),
        ("TC-09", "Open Oraimo PDP (different seller)", "Click first non-Official Store result", "Third-party seller shown", "P1", "Pass"),
        ("TC-10", "Add Oraimo to cart", "Click Add to cart", "Header shows 2 Cart", "P1", "Pass"),
        ("TC-11", "Cart summary", "Click Cart in header", "Both items; subtotal NGN 20,806", "P1", "Pass"),
        ("TC-12", "Checkout initiation", "Click Checkout", "Redirect to login/identification", "P1", "Pass"),
        ("TC-13", "Abandon before payment", "Stop at login gate", "No payment processed", "P1", "Pass"),
    ]
    add_table(
        doc,
        ["ID", "Test Case", "Steps", "Expected Result", "Priority", "Status"],
        cases,
        [0.55, 1.1, 1.5, 1.5, 0.55, 0.8],
    )

    add_heading(doc, "1.3 Tools Used", 2)
    add_table(
        doc,
        ["Tool", "Purpose"],
        [
            ["Playwright (@playwright/test)", "E2E automation — tests/jumia-checkout-flow.spec.ts"],
            ["Playwright CLI", "Interactive exploratory testing, snapshots"],
            ["Chromium (Desktop Chrome)", "Primary test browser"],
            ["Browser DevTools / Console", "JavaScript error detection"],
            ["Screenshots + video (always on)", "Evidence capture for every run"],
            ["GitHub Actions", "CI pipeline on push/PR and weekly smoke"],
            ["HTML Reporter", "Test run reporting at output/playwright/report/"],
        ],
        [2.5, 3.75],
    )

    add_heading(doc, "1.4 Estimated Duration", 2)
    add_table(
        doc,
        ["Activity", "Duration"],
        [
            ["Manual exploratory run (first pass)", "45-60 minutes"],
            ["Playwright setup and test authoring", "60-90 minutes"],
            ["Automated regression run", "~25 seconds (1 test)"],
            ["Bug documentation and report", "30-45 minutes"],
            ["TOTAL first-time completion", "3-4 hours"],
            ["Repeat regression (automated)", "Under 1 minute"],
        ],
        [3.5, 3.0],
    )

    add_heading(doc, "2. Automation Strategy", 1)

    add_heading(doc, "2.1 What Test Cases Would You Automate First (and Why)?", 2)
    doc.add_paragraph(
        "The implemented automation is a single focused Playwright spec that mirrors the manual flow: "
        "header search → click product → add to cart, repeated for both products, then cart → checkout. "
        "This keeps the test reliable and easy to debug. For a larger suite, I would extract shared "
        "helpers into page objects (POM) and add Gherkin only for stakeholder-facing happy-path scenarios."
    )
    add_table(
        doc,
        ["Automate First", "Test Cases", "Why"],
        [
            ["1st", "TC-05 to TC-11", "Core revenue path; stable DOM; no OTP"],
            ["2nd", "TC-12, TC-13", "Checkout redirect without payment"],
            ["3rd", "TC-01, TC-02", "Cookie helper in beforeEach"],
            ["4th", "TC-03, TC-04", "Once test-mailbox is wired for OTP"],
        ],
        [1.2, 1.5, 3.3],
    )

    add_heading(doc, "2.2 What Should NOT Be Automated (Manual Testing Only)?", 2)
    add_table(
        doc,
        ["Area", "Reason"],
        [
            ["OTP / email verification (TC-04)", "Requires real mailbox or test inbox API (Mailosaur, MailSlurp)"],
            ["Payment flows", "Assessment forbids payment; PCI compliance scope"],
            ["Cloudflare bot challenges", "Non-deterministic in CI; needs staging bypass"],
            ["Visual / UX review", "Promo banners, responsive layout, accessibility"],
            ["Cross-browser matrix", "Safari/Firefox payment and auth quirks"],
            ["Social login (Google/Facebook/Apple)", "OAuth popups; third-party dependency"],
            ["Seller disputes / post-checkout", "Outside core checkout funnel"],
        ],
        [2.5, 3.75],
    )

    add_heading(doc, "2.3 CI Integration Flow and Tool/Framework", 2)
    doc.add_paragraph(
        "Pipeline: Push/PR → GitHub Actions → npm ci → playwright install → npx playwright test → upload HTML report + video artifacts"
    )
    add_table(
        doc,
        ["Component", "Details"],
        [
            ["Framework", "Playwright Test (inline spec with shared helpers)"],
            ["Config", "playwright.config.ts — video and screenshots always on"],
            ["Workflow", ".github/workflows/playwright.yml"],
            ["Test spec", "tests/jumia-checkout-flow.spec.ts"],
            ["Evidence script", "npm run test:evidence — runs test and copies video to output/playwright/checkout-flow.webm"],
            ["Schedule", "Every PR + weekly smoke (Monday 06:00 UTC)"],
            ["Artifacts", "HTML report, screenshots, video (14-day retention)"],
        ],
        [1.5, 4.75],
    )

    add_heading(doc, "3. Bug Reporting", 1)

    add_heading(doc, "3.1 Issues Found During Testing", 2)
    bugs = [
        (
            "BUG-001", "Medium", "Cookie consent blocks critical interactions",
            "Cookie modal intercepts pointer events on Account, Search, and Add to cart until dismissed.",
            "1. Open jumia.com.ng (fresh session)\n2. Click Account or Search without accepting cookies",
            "Primary navigation usable", "Click timeout — modal intercepts events", "TC-02",
        ),
        (
            "BUG-002", "Low", "Recurring JS TypeError",
            "Console: TypeError: Cannot read properties of undefined (reading 'initialised'). Likely analytics script failure.",
            "Open product or cart page; inspect console", "No console errors", "Repeated TypeError", "TC-06-TC-11",
        ),
        (
            "BUG-003", "High (automation)", "Cloudflare blocks checkout/login",
            "Checkout triggers 'Performing security verification'. Automated browsers stall or fail intermittently.",
            "1. Add items to cart\n2. Click Checkout", "Smooth login redirect", "Cloudflare challenge 15-60s+", "TC-12",
        ),
        (
            "BUG-004", "Info / Design", "Guest checkout requires authentication",
            "Checkout redirects to login. No guest checkout observed.",
            "1. Add items as guest\n2. Click Checkout", "Optional guest checkout", "Login required", "TC-12",
        ),
        (
            "BUG-005", "Low", "Search relevance issue",
            "Searching 'Nivea Body Lotion' surfaces deodorant in sponsored slots before body lotions.",
            "1. Search 'Nivea Body Lotion'\n2. Review top results", "Body lotions ranked first", "Deodorant in top slots", "TC-05",
        ),
    ]
    add_table(
        doc,
        ["ID", "Severity", "Title", "Description", "Steps", "Expected", "Actual", "TC"],
        bugs,
        [0.55, 0.75, 1.0, 1.3, 1.1, 0.9, 0.9, 0.5],
    )

    add_heading(doc, "3.2 How Would You Report and Share Bugs with Engineers?", 2)
    add_bullets(doc, [
        "Create a Jira/Linear ticket with BUG-ID, severity, environment, and linked TC-ID.",
        "Attach screenshot, video (checkout-flow.webm), Playwright trace, console snippet, and exact URL.",
        "Write numbered reproduction steps any engineer can follow without QA context.",
        "Tag @engineering for P1/P2 defects; include Cloudflare Ray ID when applicable.",
        "Share a summary in Slack/Teams for fast triage.",
        "Archive the full report in Confluence/Notion and link CI artifacts.",
    ])

    add_heading(doc, "4. Traceability and Risk Mitigation", 1)

    add_heading(doc, "4.1 Traceability Matrix", 2)
    add_table(
        doc,
        ["Requirement", "Test Case", "Automation", "Status"],
        [
            ["User can sign up", "TC-03, TC-04", "Manual only — stops at OTP", "Blocked at OTP"],
            ["Search products", "TC-05, TC-08", "Automated", "Pass"],
            ["Add from 2 sellers", "TC-07, TC-10", "Automated", "Pass"],
            ["View cart", "TC-11", "Automated", "Pass"],
            ["Reach checkout", "TC-12", "Automated", "Pass"],
            ["No payment made", "TC-13", "Automated abort", "Pass"],
        ],
        [1.8, 1.2, 1.5, 1.5],
    )

    add_heading(doc, "4.2 How Do You Identify and Mitigate Risks?", 2)
    add_table(
        doc,
        ["Risk", "Likelihood", "Impact", "Mitigation"],
        [
            ["Cloudflare blocks CI", "High", "High", "storageState; off-peak runs; staging bypass"],
            ["OTP/email dependency", "High", "Medium", "Mailosaur integration; mock auth in staging"],
            ["Cookie modal flakiness", "Medium", "Medium", "acceptCookies() helper before each action"],
            ["Product URLs change", "Medium", "Low", "Search-then-pick pattern (no hardcoded URLs)"],
            ["Price/stock drift", "Medium", "Low", "Assert structure not exact price"],
            ["Multi-seller shipping split", "Low", "Medium", "Manual test delivery fees at checkout"],
            ["Accidental payment", "Low", "Critical", "Abort at login gate; never store card data"],
        ],
        [1.8, 0.8, 0.8, 2.6],
    )

    add_heading(doc, "4.3 How Do You Ensure Traceability?", 2)
    add_bullets(doc, [
        "Test Case IDs (TC-01 to TC-13) map to automation spec and manual charters.",
        "Playwright test name documents the exact flow: Nivea + Oraimo via top search, cart, checkout.",
        "Git commits link automation code to this assessment deliverable.",
        "CI artifacts (HTML report, screenshots, video) retained for 14 days.",
        "BUG-XXX references TC-XX in the defect tracking system.",
    ])

    add_heading(doc, "5. Recommendations", 1)
    add_table(
        doc,
        ["Audience", "Recommendation", "Rationale"],
        [
            ["Product", "Offer guest checkout", "Users abandon at login wall"],
            ["Product", "Improve search relevance for body lotion", "Deodorant surfaced before lotions"],
            ["Product", "Per-seller shipping estimates in cart", "Multi-seller carts need delivery clarity"],
            ["Product", "Non-blocking cookie banner", "Modal blocks Account, Search, Add to cart"],
            ["Engineering", "Fix 'initialised' TypeError in tracking scripts", "Silent analytics failure"],
            ["Engineering", "Add data-testid on key elements", "Stabilises automation selectors"],
            ["Engineering", "Staging/UAT without Cloudflare", "Unblocks CI and OTP testing"],
            ["Engineering", "API-level cart/session test hooks", "Faster integration tests beneath E2E"],
            ["QA", "Mailosaur for OTP in CI", "Completes sign-up automation path"],
            ["QA", "Extract POM from helpers once suite grows", "Maintainability at scale"],
            ["QA", "Visual regression on PDP and cart", "Catch layout regressions early"],
            ["QA", "Quarterly Firefox + WebKit runs", "Cross-browser coverage"],
        ],
        [1.1, 2.5, 2.4],
    )

    add_heading(doc, "6. Automation Evidence", 1)
    doc.add_paragraph(
        "The Playwright test records video on every run. Regenerate evidence with:"
    )
    doc.add_paragraph("npm run test:evidence", style="Intense Quote")
    doc.add_paragraph(
        f"Video file (attach to submission email): {VIDEO_PATH}\n"
        "Screenshots are embedded below and also saved under output/playwright/."
    )

    add_heading(doc, "6.1 Cart — Two Sellers", 2)
    add_image_if_exists(doc, CART_SHOT, "Cart with Nivea (Official Store) and Oraimo (third-party seller) — NGN 20,806")

    add_heading(doc, "6.2 Checkout — Login Gate (Abandoned)", 2)
    add_image_if_exists(doc, CHECKOUT_SHOT, "Checkout redirected to login — no payment made")

    add_heading(doc, "6.3 Video Recording", 2)
    doc.add_paragraph(
        f"Full E2E run video: {VIDEO_PATH} (WebM format — attach this file to the submission email alongside the Word document). "
        "Word cannot embed WebM video; open the file in VLC, QuickTime, or any browser."
    )

    doc.add_paragraph()
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    f = footer.add_run(
        "Assessment completed against https://www.jumia.com.ng/. "
        "No payment was made. Order abandoned at login/checkout gate as instructed."
    )
    f.italic = True
    f.font.size = Pt(9)

    doc.save(OUTPUT)
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    build()
