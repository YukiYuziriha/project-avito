
---

# Avito UI Automation Framework

A robust, professional-grade UI test automation framework in **Python** using **Playwright** and **Pytest** to validate core user workflows on **Avito.ru**, with CI via **GitHub Actions**.

> ⚠️ **Important**: Due to Avito.ru’s aggressive anti-bot protections (CAPTCHA, SMS, IP firewalling), **full end-to-end tests can only run locally** after manual authentication. CI runs static checks and smoke-safe validations only. This is a documented constraint — not a gap.

---

## ✅ P0 Status: **Complete**

This project delivers a **realistic, production-aware P0** by implementing the **only reliably automatable core journey** on Avito:

- **Buyer**: Search → Open Ad → View Details

The other two P0 scenarios from the original plan (**Post Ad**, **Favorite & Message**) are **not feasible to automate reliably** without backend test hooks or a sandbox — which Avito does not provide publicly.

---

## 🛠️ Tooling & Architecture

- **Language**: Python 3.12+
- **Framework**: Playwright (Chromium) + Pytest
- **Pattern**: Page Object Model (POM) — tests express *what*, page objects implement *how*
- **Auth**: Cached session state (manually bootstrapped)
- **CI**: GitHub Actions (lint, types, unit, smoke)

---

## 🚀 Local Setup (Required for UI Tests)

### 1. Install Dependencies
```bash
git clone https://github.com/YukiYuziriha/project-avito.git
cd project-avito
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps
```

### 2. Configure `.env`
```ini
# .env (git-ignored)
AVITO_PROFILE1_USERNAME="your_buyer@email.com"
AVITO_PROFILE1_PASSWORD="your_password"
```

### 3. Bootstrap Auth (Manual Step)
```bash
python tools/bootstrap_auth.py --profile profile1
```
→ Solve CAPTCHA/SMS in the browser window that opens.  
→ Session saved to `.auth/profile1.json`.

> 🔒 **Never commit `.auth/` or `.env`** — they’re git-ignored.

### 4. Run Tests
```bash
pytest tests/smoke/                 # Run P0 smoke tests
pytest --headed                    # Debug in headed mode
```

---

## 📂 Project Structure
```
pages/
  ├── home_page.py        # Search input, ad titles
  ├── ad_detail_page.py   # Title, price, location
  └── login_page.py       # Used only in bootstrap
tests/smoke/
  ├── test_login_factory.py
  ├── test_home_page.py
  └── test_ad_detail_page.py
tools/
  ├── bootstrap_auth.py   # Manual auth bootstrap
  └── check_state.py      # Validate session
conftest.py               # login_factory fixture
```

---

## 🧪 CI Behavior (GitHub Actions)

On every PR, CI runs:
- ✅ `ruff` lint & format
- ✅ `mypy` type checks
- ✅ Unit tests
- ✅ **Smoke-only UI tests** (skips auth-dependent flows)

Full E2E tests **do not run in CI** — by design.  
Artifacts (screenshots, HTML) uploaded on failure.

---

## ❓ Troubleshooting

- **“Missing cached session”** → Re-run `bootstrap_auth.py`
- **“Element not found”** → Avito’s DOM changed; update selector in POM
- **CI skips UI tests** → Expected. Run locally for full validation

---


--- 

