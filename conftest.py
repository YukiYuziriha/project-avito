# conftest.py
import json
from pathlib import Path
import pytest
from playwright.sync_api import Browser, Page
from dotenv import load_dotenv, find_dotenv

# --- Paths / env -------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
load_dotenv(find_dotenv())                    # keep for other fixtures if needed
AUTH_DIR = ROOT / ".auth"
AUTH_DIR.mkdir(exist_ok=True)
DATA_DIR = ROOT / "test_data"
USERS_JSON = DATA_DIR / "test_users.json"

# Remember which roles we've already validated this session
_STATE_VALIDATED: dict[str, bool] = {}

# --- Small helpers (no login attempts here) ----------------------------------
def _state_file_for(role: str) -> Path:
    return AUTH_DIR / f"{role}.json"

def _click_continue_if_present(page: Page) -> None:
    try:
        page.get_by_text("Продолжить", exact=True).first.click(timeout=1000)
    except Exception:
        pass

def _looks_logged_in(page: Page) -> bool:
    """
    True only when session is actually authorized.
    Not logged in if:
      - URL contains /profile/login
      - login inputs are present
    Positive signal: 'Мой профиль' or any /profile without /login.
    """
    url = page.url.lower()
    if "profile/login" in url:
        return False
    # login form visible => definitely not authorized
    if page.locator("input[name='login']").count() or page.locator("input[type='password']").count():
        return False
    # strong positive signal
    if page.locator("text=Мой профиль").count():
        return True
    # weak positive (profile url without /login)
    return ("profile" in url) and ("login" not in url)

def _validate_state_once(browser: Browser, role: str, state_file: Path) -> None:
    """
    Open a temporary context with the saved state and verify we're truly logged in.
    If invalid, fail with a clear message telling how to create the state.
    """
    # Already validated in this pytest session
    if _STATE_VALIDATED.get(role):
        return

    ctx = browser.new_context(storage_state=str(state_file))
    page = ctx.new_page()
    try:
        page.goto("https://www.avito.ru/profile", timeout=60_000)
        _click_continue_if_present(page)

        # short settle loop (~5s)
        for _ in range(10):
            if _looks_logged_in(page):
                _STATE_VALIDATED[role] = True
                return
            page.wait_for_timeout(500)
            _click_continue_if_present(page)

        # If we get here, the state is not valid
        pytest.fail(
            f"Cached session is invalid for role '{role}': {state_file}\n"
            f"Create/refresh it manually:\n"
            f"    python tools/bootstrap_auth.py\n"
            f"(Browser will open → solve CAPTCHA + SMS → press ENTER to save state.)"
        )
    finally:
        ctx.close()

# --- Fixtures ----------------------------------------------------------------
@pytest.fixture(scope="session")
def test_users() -> dict:
    if USERS_JSON.exists():
        with open(USERS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@pytest.fixture
def login_factory(browser: Browser, request: pytest.FixtureRequest):
    """
    Usage:
        page = login_factory("buyer")    # requires .auth/buyer.json
        page = login_factory("seller")   # requires .auth/seller.json

    Behavior:
      - If state file is missing -> fail with a clear instruction to run the bootstrap script.
      - If present -> validate once per role (no login attempt).
      - Always returns a Page with the cached state applied.
    """
    def _login(role: str = "buyer", *, reuse_state: bool = True) -> Page:
        role = role.lower().strip()
        state_file = _state_file_for(role)

        if reuse_state:
            if not state_file.exists():
                pytest.fail(
                    f"Missing cached session for role '{role}': {state_file}\n"
                    f"Create it manually:\n"
                    f"    python tools/bootstrap_auth.py"
                )
            # Validate once per role (no login attempt)
            _validate_state_once(browser, role, state_file)
            # Now open a fresh context for the test itself
            ctx = browser.new_context(storage_state=str(state_file))
        else:
            # Raw context (no auth)
            ctx = browser.new_context()

        page = ctx.new_page()
        request.addfinalizer(ctx.close)
        return page

    return _login
