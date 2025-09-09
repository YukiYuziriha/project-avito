#conftest.py
import json
import os
from pathlib import Path
import pytest
from playwright.sync_api import Page, Browser

#Define paths
DATA_DIR = Path(__file__).parent / "test_data"
USERS_JSON = DATA_DIR / "test_users.json"
AUTH_DIR = Path(__file__).parent / ".auth" #Directory to store authentication states
AUTH_DIR.mkdir(exist_ok=True) #Existance check

def _do_login(page: Page, username: str, password: str) -> None:
    
    """
    Helper function to perform the login UI flow on Avito.ru.
    Encapsulates UI interactions for logging in.
    """
    
    page.goto("https://www.avito.ru/profile/login")
    page.fill('input[name="login"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    #Wait for login to complete: check for profile URL and element
    page.wait_for_url("**/profile/**", timeout=15000)
    page.wait_for_selector("text=Мой профиль", timeout=15000)

@pytest.fixture(scope="session")
def test_users() -> dict:
    """
    Session-scoped fixture to load test users from JSON file.
    Reads credentials once per test session for efficiency.
    """
    with open(USERS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)
    
@pytest.fixture
def login_factory(browser: Browser, test_users: dict):
    """
    Fixture that returns a callable function to log in a user.

    Args:
        role_or_user: Either a string key from test_users (e.g., 'buyer') or a dict with 'username' and 'password'.
        new_context: If True, creates a new browser context for isolation (essential for multi-user tests).
        reuse_state: If True, reuses cached authentication state to speed up login.

    Returns:
        Page: A Playwright Page object authenticated as the requested user.
    """
    def _login(role_or_user, *, new_context=False, reuse_state=True) -> Page:
        #Resolve credentials: check for env vars or use test_users.json
        if isinstance(role_or_user, str):
            env_username = os.getenv(f"AVITO_{role_or_user.upper()}_USERNAME")
            env_password = os.getenv(f"AVITO_{role_or_user.upper()}_PASSWORD")
            if env_username and env_password:
                creds = {"username": env_username, "password": env_password}
            else:
                creds = test_users[role_or_user]
        else:
            creds = role_or_user

        username = creds["username"]
        state_file = AUTH_DIR / f"{username}.json"

        # Reuse stored authentication state if available and requested
        if reuse_state and state_file.exists():
            context = browser.new_context(storage_state=str(state_file))
            return context.new_page()

        # Create a new context for login (isolated if new_context=True) 
        context = browser.new_context()
        page = context.new_page()
        _do_login(page, username, creds["password"])

        if reuse_state:
            context.storage_state(path=str(state_file))

        return page
    
    return _login
