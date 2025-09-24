# Avito UI Automation Framework

A robust UI test automation framework in **Python** using **Playwright** and **Pytest** to validate key user workflows on **Avito.ru**, with CI via **GitHub Actions**.

## Objectives
- Prove a **maintainable, professional** automation system.
- Cover **core end-to-end** user journeys.
- Run reliably in **CI on every PR**, producing clear, developer-friendly feedback.
- Demonstrate senior-level choices: clean architecture and professional delivery.

## Project Plan
- **Tooling:** Python, Playwright and Pytest with a Page Object Model architecture.
- **Scenarios:** Buyer search & filter, seller post ad, buyer favourite & message seller.
- **Data:** Small JSON datasets and fixtures for deterministic test users.
- **CI:** GitHub Actions pipeline running tests on every pull request.

## Current Status
- Core page objects and fixtures are implemented in `pages/` and `conftest.py`.
- Tests for the three core journeys live under `tests/` and run locally with a cached auth state.
- GitHub Actions workflow (`.github/workflows/tests.yml`) executes non-auth tests on PRs.
- Authentication bootstrap script (`tools/bootstrap_auth.py`) prepares session state for full E2E runs.

---

## Local Development Setup

This project requires a one-time manual authentication step to generate a local session file. This file is used by the test suite to bypass the UI login, which is often protected by CAPTCHA.

### **Step 1: Install Dependencies**

1.  Clone the repository and navigate to the project root.
2.  Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    playwright install --with-deps
    ```
### **Step 2: Create `.env` File**

Create a `.env` file in the project root by copying the `.env.example`. Fill it with your test account credentials using the scalable `PROFILEN` convention.

```ini
# .env
# Credentials for different test profiles
AVITO_PROFILE1_USERNAME="<login_for_profile1>"
AVITO_PROFILE1_PASSWORD="<password_for_profile1>"

AVITO_PROFILE2_USERNAME="<login_for_profile2>"
AVITO_PROFILE2_PASSWORD="<password_for_profile2>"
````

### **Step 3: Generate Authentication State**

Run the interactive bootstrap script to log in manually and save the session state. A browser window will open for you to solve any CAPTCHAs and enter SMS codes.

  * **To log in as `profile1`**:
    ```bash
    python tools/bootstrap_auth.py --profile profile1
    ```
  * **To re-authenticate even if the session is still valid**:
    ```bash
    python tools/bootstrap_auth.py --profile profile1 --force
    ```

The script will first check if a valid session already exists. If so, it will do nothing. After you log in, it saves a `profilename.json` file to the `.auth/` directory.

### **Step 4: Run Tests**

You can now run the Pytest suite. The tests will automatically use the cached authentication state, which is validated once per run.

  * **Run all tests**:
    ```bash
    pytest
    ```
  * **Run tests in parallel and in headed mode**:
    ```bash
    pytest -n auto --headed
    ```
  * **Run tests in a specific file**:
    ```bash
    pytest tests/test_search_filters.py
    ```

-----

## Project Structure

```
profile
Qwen3-Max
5:07 pm
✅ Updated README Section: Project Structure
Replace the existing Project Structure section in your README.md with this updated version:

markdown


1
2
## Project Structure

.
├── .auth/ # Stores cached authentication state (git-ignored)
├── artifacts/ # Stores debug output like screenshots and traces (git-ignored)
├── pages/ # Page Object Model files
├── tests/
│ ├── smoke/ # Smoke tests (e.g., auth integration)
│ └── <feature>/ # Feature-specific UI tests (e.g., search, messaging)
├── test_data/ # Test data files (e.g., test_users.json)
├── tools/ # Helper and utility scripts
│ ├── bootstrap_auth.py # Interactive script to create auth state
│ └── check_state.py # Utility to validate an existing auth state
├── .env # Local environment variables (git-ignored)
├── .env.example # Template for environment variables
├── conftest.py # Pytest fixtures and test configuration
├── pytest.ini # Pytest configuration
└── requirements.txt # Project dependencies
```
