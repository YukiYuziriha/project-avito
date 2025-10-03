# Automating the Unautomatable: A Case Study in Testing Hostile Web Environments

This project is a professional-grade UI test automation framework for **Avito.ru**. It's not just a set of test scripts; it's a case study in engineering a resilient and maintainable solution for a real-world, high-security, and actively hostile target platform.

The primary goal was to solve a senior-level problem: **How do you test a system that is designed to prevent automation?**

-----

## The Core Challenge: Avito's Anti-Bot Reality

Avito.ru employs aggressive anti-automation measures that make traditional testing approaches impossible. Any robust test strategy *must* acknowledge and engineer around these constraints:

  - **Intrusive Bot Detection:** CAPTCHA, SMS verification, and device fingerprinting block all unattended login attempts.
  - **IP-Based Firewalling:** Automated requests from datacenter IPs (like GitHub Actions runners) are instantly blocked.
  - **Ephemeral Sessions:** Authentication states are short-lived and cannot be reliably reused across different environments or long periods.

**Conclusion:** End-to-end UI tests that require login **cannot be run in a standard CI/CD pipeline.** This is a fundamental constraint of the target platform, not a limitation of the framework.

-----

## Architectural Solution & Strategy

This framework demonstrates a mature, pragmatic approach to these challenges.

  - **Pattern:** Strict Page Object Model (POM) to decouple test logic from fragile UI selectors, ensuring maintainability.
  - **Authentication:** A `bootstrap_auth.py` utility handles the **one-time manual login process**. It solves the CAPTCHA/SMS problem by allowing a human to intervene and then saves the authenticated session state. This cached state is then reused by the `login_factory` fixture across all local test runs.
  - **Test Scope:** The test suite is deliberately focused on the **read-only "Buyer Journey"** (Search → View Ad). This is the only high-value workflow that can be automated with any degree of stability. Scenarios requiring state changes (Posting Ads, Messaging) were scoped out as they are untestable without official API access.

-----

## 🚀 Local Execution: The Only Way to Run

All UI tests are **local-only by design**. This is the only environment where the manually bootstrapped authentication state is valid.

### 1\. Install Dependencies

```bash
git clone https://github.com/YukiYuziriha/project-avito.git
cd project-avito
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps
```

### 2\. Configure Environment

Create a `.env` file (git-ignored) with your credentials:

```ini
# .env
AVITO_PROFILE1_USERNAME="your_buyer@email.com"
AVITO_PROFILE1_PASSWORD="your_password"
```

### 3\. Bootstrap Authentication (One-Time Manual Step)

Run this command. A browser will open, allowing you to solve any CAPTCHAs and complete the login.

```bash
python tools/bootstrap_auth.py --profile profile1
```

The authenticated session will be saved to `.auth/profile1.json`.

### 4\. Run the Test Suite

```bash
# Run all smoke tests
pytest tests/smoke/

# Run in headed mode for debugging
pytest --headed
```

-----

## 🧪 CI/CD: A Strategy of Safety and Realism

The GitHub Actions pipeline for this project is intentionally limited to tasks that can be run safely and reliably:

  - ✅ **Static Analysis:** `ruff` for linting/formatting and `mypy` for type checking.
  - ✅ **Code Health:** Unit tests and dependency checks.

**The CI pipeline does NOT run UI tests.** Attempting to do so would result in guaranteed failures due to Avito's security, creating noise and providing no value. This represents a professional decision to maintain a green, trustworthy CI pipeline.

-----

## 📂 Project Structure

```
pages/          # Page Object Models: Decoupled UI interactions
tests/smoke/    # Pytest tests: The business logic and assertions
tools/          # Helper scripts for auth and state management
conftest.py     # Core Pytest fixtures (e.g., login_factory)
.github/        # CI workflow definitions
```