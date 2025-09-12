# conftest.py
import json
from pathlib import Path
import pytest
from playwright.sync_api import Browser, Page
from dotenv import load_dotenv, find_dotenv
from filelock import FileLock, Timeout

# --- Paths / env -------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
load_dotenv(find_dotenv())
AUTH_DIR = ROOT / ".auth"
AUTH_DIR.mkdir(exist_ok=True)
DATA_DIR = ROOT / "test_data"
USERS_JSON = DATA_DIR / "test_users.json"

# Remember which profiles we've already validated this session
_STATE_VALIDATED: dict[str, bool] = {}


# --- Small helpers (no login attempts here) ----------------------------------
def _state_file_for(profile: str) -> Path:
    """Generates the expected path for a profile's saved auth state."""
    return AUTH_DIR / f"{profile}.json"


def _click_continue_if_present(page: Page) -> None:
    """Clicks the 'Continue' button if it appears after navigation."""
    try:
        page.get_by_text("Продолжить", exact=True).first.click(timeout=1000)
    except Exception:
        pass


def _looks_logged_in(page: Page) -> bool:
    """Heuristically checks if the page session is authenticated."""
    url = page.url.lower()
    if "profile/login" in url:
        return False
    # Login form visible => definitely not authorized
    if page.locator("input[name='login']").count() or page.locator("input[type='password']").count():
        return False
    # Strong positive signal
    if page.locator("text=Мой профиль").count():
        return True
    # Weak positive signal (profile URL without /login)
    return "profile" in url and "login" not in url


def _validate_state_once(browser: Browser, profile: str, state_file: Path) -> None:
    """
    (Process-safe) Opens a temporary context to verify the session is active.
    If invalid, deletes the bad state file and fails with a clear message.
    """
    if _STATE_VALIDATED.get(profile):
        return

    lock_file = state_file.with_suffix(".json.lock")
    try:
        with FileLock(str(lock_file), timeout=120):
            # After acquiring lock, another process might have already validated.
            if _STATE_VALIDATED.get(profile):
                return

            ctx = browser.new_context(storage_state=str(state_file))
            page = ctx.new_page()
            try:
                page.goto("https://www.avito.ru/profile", timeout=60_000)
                _click_continue_if_present(page)

                for _ in range(10):
                    if _looks_logged_in(page):
                        _STATE_VALIDATED[profile] = True
                        return
                    page.wait_for_timeout(500)
                    _click_continue_if_present(page)

                # State is invalid: delete the file before failing
                try:
                    state_file.unlink()
                    print(f"\n[auth] Deleted invalid state file: {state_file}")
                except OSError as e:
                    print(f"\n[auth] Warning: Could not delete invalid state file: {e}")

                pytest.fail(
                    f"Cached session is invalid for profile '{profile}'. The bad file has been deleted.\n"
                    f"Please create a new one by running:\n"
                    f"    python tools/bootstrap_auth.py --profile {profile}"
                )
            finally:
                ctx.close()
    except Timeout:
        pytest.fail(f"Could not acquire lock for state validation '{lock_file}' after 2 minutes.")


# --- Fixtures ----------------------------------------------------------------
@pytest.fixture(scope="session")
def test_users() -> dict:
    """Loads test user data from a JSON file."""
    if USERS_JSON.exists():
        with open(USERS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@pytest.fixture
def login_factory(browser: Browser, request: pytest.FixtureRequest):
    """
    A factory fixture to get a logged-in Page object for a specific test profile.

    Usage:
        page = login_factory("profile1")
        page = login_factory("profile2")

    Behavior:
      - Fails with a clear error if the required auth file is missing.
      - (Process-safe) Validates the auth file once per profile per test run.
      - Returns a new, clean Page object with the cached auth state applied.
    """
    def _login(profile: str = "profile1", *, reuse_state: bool = True) -> Page:
        profile = profile.lower().strip()
        state_file = _state_file_for(profile)

        if reuse_state:
            if not state_file.exists():
                pytest.fail(
                    f"Missing cached session for profile '{profile}': {state_file}\n"
                    f"Create it manually:\n"
                    f"    python tools/bootstrap_auth.py --profile {profile}"
                )
            _validate_state_once(browser, profile, state_file)
            ctx = browser.new_context(storage_state=str(state_file))
        else:
            ctx = browser.new_context()

        page = ctx.new_page()
        request.addfinalizer(ctx.close)
        return page

    return _login