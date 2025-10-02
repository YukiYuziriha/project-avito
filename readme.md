```markdown
# Avito UI Automation Framework

A robust, professional-grade UI test automation framework in **Python** using **Playwright** and **Pytest** to validate core user workflows on **Avito.ru**, with CI via **GitHub Actions**.

## Objectives

- ✅ Prove a **maintainable, professional** automation system (not just scripts).
- ✅ Cover **core end-to-end** user journeys that reflect real Avito usage.
- ✅ Run reliably in **CI on every PR**, producing clear, developer-friendly feedback.
- ✅ Demonstrate senior-level engineering: clean architecture, right tooling, and delivery discipline.

## Current Scope (Phase 1 — P0 Complete)

This project implements **one verified P0 user journey**:

- **Buyer**: Search → open ad → view ad details

> **Note**: Seller (post ad) and engagement (favorite & message) flows are **planned for Phase 2** and are **not part of current P0 scope**.

## Tooling & Architecture

- **Language**: Python 3.12+
- **Framework**: Playwright (Chromium) + Pytest
- **Pattern**: Page Object Model (POM) — tests express *what*, page objects implement *how*
- **CI**: GitHub Actions (smoke tests on every PR)
- **Auth**: Cached session state (manual bootstrap due to CAPTCHA/anti-bot)

## Local Development Setup

This project requires a **one-time manual authentication step** to generate a local session file. This bypasses CAPTCHA-protected login during test runs.

### Step 1: Install Dependencies

```bash
# Clone and enter project
git clone https://github.com/YukiYuziriha/project-avito.git
cd project-avito

# Virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .\.venv\Scripts\activate  # Windows

# Install deps
pip install -r requirements.txt
playwright install --with-deps
```

### Step 2: Configure `.env`

Copy `.env.example` to `.env` and fill credentials for test profiles:

```ini
# .env
AVITO_PROFILE1_USERNAME="your_buyer_login"
AVITO_PROFILE1_PASSWORD="your_buyer_password"
```

> 🔒 **Never commit `.env`** — it’s git-ignored.

### Step 3: Bootstrap Authentication State

Run the interactive script to log in manually (solve CAPTCHA/SMS):

```bash
python tools/bootstrap_auth.py --profile profile1
```

This saves `.auth/profile1.json`, which tests reuse.

> ⚠️ **Automated login is impossible** due to Avito’s anti-bot protections. Manual bootstrap is the only reliable method.

### Step 4: Run Tests

```bash
# Run all tests (uses cached auth)
pytest

# Run smoke tests only
pytest tests/smoke/

# Run in headed mode (for debugging)
pytest --headed

# Run in parallel
pytest -n auto
```

Auth-dependent tests automatically skip in CI (see `pytest.ini`).

---

## Project Structure

```
.
├── .auth/                 # Cached auth state (git-ignored)
├── artifacts/             # Debug output: screenshots, traces (git-ignored)
├── pages/                 # Page Objects (POM)
│   ├── home_page.py       # Search, results interaction
│   ├── ad_detail_page.py  # Ad title, price, location
│   └── login_page.py      # Login form (used only in bootstrap)
├── tests/
│   └── smoke/             # P0 smoke tests (auth integration)
├── test_data/             # Test data (e.g., test_users.json)
├── tools/
│   ├── bootstrap_auth.py  # Interactive auth state creation
│   └── check_state.py     # Validate saved session
├── conftest.py            # Pytest fixtures (browser, login_factory)
├── pytest.ini             # Test config (markers, timeouts)
├── requirements.txt       # Dependencies
├── .env.example           # Env template
└── README.md              # You are here
```

---

## Quality & Compliance

- ✅ **POM-compliant**: No raw selectors in tests.
- ✅ **Auth-safe**: Credentials never committed; session state reused.
- ✅ **Flake-resistant**: Playwright auto-waits + explicit `expect` conditions.
- ✅ **CI-ready**: Smoke tests run on every PR (`ui-smoke` marker).
- ✅ **Documented**: This README covers setup, scope, and constraints.

---

## CI/CD (GitHub Actions)

- **Trigger**: On every `pull_request` to `main`
- **Jobs**: 
  - Lint (`ruff`), type-check (`mypy`)
  - Unit tests
  - UI smoke tests (headless, with 1 retry)
- **Artifacts**: Screenshots + HTML on failure (via `artifacts/`)
- **Auth tests**: Skipped in CI using `pytest -m "not auth"`

> 🔜 **Phase 2**: Enable full E2E suite in nightly runs with pre-seeded auth.

---

## P0 Verification

| Requirement | Status |
|-----------|--------|
| Buyer: search → open ad → view details | ✅ Implemented |
| Page Objects for core flows | ✅ `HomePage`, `AdDetailPage` |
| Auth state management | ✅ Manual bootstrap + validation |
| CI runs smoke tests on PRs | ✅ `ui-smoke` marker |
| README with setup & scope | ✅ This document |

---

## Next Steps (Phase 2)

- [ ] Implement **Seller: Post Ad** flow
- [ ] Implement **Engagement: Favorite & Message**
- [ ] Add `SearchResultsPage` if filter logic grows
- [ ] Enable nightly full E2E runs in CI
- [ ] Add `CONTRIBUTING.md`, `CODEOWNERS`, `CHANGELOG.md`

---

## Troubleshooting

- **“Missing cached session”**: Run `bootstrap_auth.py` again.
- **Test fails to find ad title**: Avito’s DOM may have changed — update selector in `HomePage`.
- **CAPTCHA appears in bootstrap**: Complete it manually in the browser window.
- **CI skips auth tests**: Expected. Run locally to validate full flow.

---

> **“A test is only as good as its ability to survive change.”**  
> — This framework prioritizes **maintainability** over coverage breadth.
```