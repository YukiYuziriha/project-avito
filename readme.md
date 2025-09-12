# Avito UI Automation Framework

A robust UI test automation framework in **Python** using **Playwright** and **Pytest** to validate key user workflows on **Avito.ru**, with CI via **GitHub Actions**.

## Objectives

  - Prove a **maintainable, professional** automation system.
  - Cover **core end-to-end** user journeys.
  - Run reliably in **CI on every PR**, producing clear, developer-friendly feedback.
  - Demonstrate senior-level choices: clean architecture and professional delivery.

-----

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

Create a `.env` file in the project root by copying the `.env.example`. Fill it with your test account credentials. You can provide credentials for different roles (`buyer`, `seller`) or a generic fallback.

```ini
# .env
# Credentials for the 'buyer' role
AVITO_BUYER_USERNAME="your_buyer_login"
AVITO_BUYER_PASSWORD="your_buyer_password"

# Credentials for the 'seller' role
AVITO_SELLER_USERNAME="your_seller_login"
AVITO_SELLER_PASSWORD="your_seller_password"
```

### **Step 3: Generate Authentication State**

Run the interactive bootstrap script to log in manually and save the session state. A browser window will open, and you must solve any CAPTCHAs and enter SMS codes.

  * To log in as the **buyer**:
    ```bash
    python tools/bootstrap_auth.py --role buyer
    ```
  * To log in as the **seller**:
    ```bash
    python tools/bootstrap_auth.py --role seller
    ```

After you are successfully logged in within the browser, press **Enter** in your terminal. This will save a `buyer.json` or `seller.json` file to the `.auth/` directory. These files are git-ignored.

### **Step 4: Run Tests**

You can now run the Pytest suite. The tests will automatically use the cached authentication state.

```bash
# Run all tests
pytest

# Run tests in headed mode to watch the browser
pytest --headed

# Run a specific test file
pytest tests/test_search_filters.py
```

-----

## Project Structure

```
.
├── .auth/                  # Stores cached authentication state (git-ignored)
├── artifacts/              # Stores debug output like screenshots (git-ignored)
├── pages/                  # Page Object Model files (e.g., home_page.py)
├── tests/                  # Test files (e.g., test_search.py)
├── test_data/              # Test data files (e.g., test_users.json)
├── tools/                  # Helper and utility scripts
│   ├── bootstrap_auth.py   # Interactive script to create auth state
│   └── check_state.py      # Utility to validate an existing auth state
├── .env                    # Local environment variables (git-ignored)
├── .env.example            # Template for environment variables
├── conftest.py             # Pytest fixtures and test configuration
├── pytest.ini              # Pytest configuration
└── requirements.txt        # Project dependencies
