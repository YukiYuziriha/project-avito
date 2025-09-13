# tools/bootstrap_auth.py
from pathlib import Path
import os
import sys
import time
import argparse
from dotenv import load_dotenv, find_dotenv
from playwright.sync_api import sync_playwright, Page, Playwright, TimeoutError as PWTimeout

# --- Setup -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(find_dotenv())

AUTH_DIR = ROOT / ".auth"
AUTH_DIR.mkdir(exist_ok=True)

ART_DIR = ROOT / "artifacts"
ART_DIR.mkdir(exist_ok=True)

BASE_URL = os.getenv("AVITO_BASE_URL", "https://www.avito.ru")
HEADLESS = bool(int(os.getenv("AVITO_HEADLESS", "0")))

# Import the check function
sys.path.append(str(ROOT / "tools"))
from check_state import check as check_state_validity

# Import LoginPage POM
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from pages.login_page import LoginPage

# --- Helpers -----------------------------------------------------------------
def get_last_profile(default="profile1") -> str:
    """Reads the last used profile from a hint file for a sensible default."""
    hint_file = AUTH_DIR / ".last_profile"
    if hint_file.exists():
        profile = hint_file.read_text(encoding="utf-8").strip().lower()
        if profile:
            return profile
    return default

def resolve_creds(profile: str):
    """Resolves credentials for a given profile from environment variables."""
    profile_up = profile.upper()
    user = os.getenv(f"AVITO_{profile_up}_USERNAME") or os.getenv("AVITO_USERNAME")
    pwd = os.getenv(f"AVITO_{profile_up}_PASSWORD") or os.getenv("AVITO_PASSWORD")
    if not (user and pwd):
        raise RuntimeError(
            f"Missing credentials for profile '{profile}'. "
            f"Set AVITO_{profile_up}_USERNAME/PASSWORD or AVITO_USERNAME/AVITO_PASSWORD in .env"
        )
    return user, pwd

def is_logged_in(page: Page) -> bool:
    """Heuristically checks if the page session is authenticated."""
    url = page.url.lower()
    if "profile/login" in url:
        return False
    if page.locator("input[name='login']").count() or page.locator("input[type='password']").count():
        return False
    if page.locator("text=Мой профиль").count():
        return True
    return "profile" in url and "login" not in url

def save_artifacts(page: Page, profile: str, reason: str):
    """Save screenshot + HTML for debugging bootstrap failures."""
    ts = int(time.time())
    base = f"bootstrap_{profile}_{reason}_{ts}"
    try:
        png = ART_DIR / f"{base}.png"
        html = ART_DIR / f"{base}.html"
        page.screenshot(path=str(png), full_page=True)
        html.write_text(page.content(), encoding="utf-8")
        print(f"[bootstrap] Saved artifacts: {png.name}, {html.name}")
    except Exception as e:
        print(f"[bootstrap] Could not save artifacts: {e}")

# --- Main Logic --------------------------------------------------------------
def run_login_flow(p: Playwright, profile: str, state_file: Path):
    """Handles the browser interaction for logging in and saving state."""
    user, pwd = resolve_creds(profile)
    browser = p.chromium.launch(
        headless=HEADLESS,
        args=["--disable-blink-features=AutomationControlled"]
    )
    ctx = browser.new_context()
    page = ctx.new_page()
    page.set_default_timeout(20_000)

    try:
        print(f"\n[bootstrap] Attempting to log in as profile: '{profile}'...")

        # --- USE THE POM HERE ---
        lp = LoginPage(page)
        lp.navigate()
        lp.login(user, pwd)
        # ------------------------

        if sys.stdin.isatty():
            # Interactive mode for local development
            print(f"\n[bootstrap:{profile}] A browser window has opened.")
            print(">>> Solve CAPTCHA / enter SMS code and finish login.")
            print(">>> When profile page is fully visible, press ENTER here to save the session.")
            print(">>> NOTE: You might need to press ENTER more than once if you are not yet on your profile page.\n")
            while True:
                input("[bootstrap] Press ENTER to verify login and save (may not work until your profile page is visible)... ")
                try:
                    page.wait_for_load_state('networkidle', timeout=5_000)
                    # Always navigate to /profile to check state after pressing ENTER
                    page.goto(f"{BASE_URL}/profile", timeout=30_000)
                    page.wait_for_load_state('networkidle', timeout=10_000)
                except Exception:
                    pass
                try:
                    if is_logged_in(page):
                        break
                except Exception:
                    # Retry ONCE in case of context lost during navigation
                    time.sleep(1)
                    try:
                        if is_logged_in(page):
                            break
                    except Exception:
                        print("[bootstrap] Playwright navigation in progress. Please press ENTER again if your profile page is visible.")
                        continue
                print("[bootstrap] Still not logged in. Finish login (or navigate to your profile), then press ENTER again.")
        else:
            # Non-interactive mode for CI/CD (shouldn't be needed for manual use)
            print("\n[bootstrap] No TTY detected. Auto-waiting up to 10 minutes for login...")
            try:
                page.wait_for_url("**/profile/**", timeout=600_000)
                page.wait_for_load_state('networkidle', timeout=15_000)
            except PWTimeout:
                save_artifacts(page, profile, "timeout")
                raise TimeoutError("Login was not detected within the 10-minute window.")

        # Final verification before saving
        if not is_logged_in(page):
            save_artifacts(page, profile, "invalid")
            raise RuntimeError("Login check failed. Refusing to save an invalid state.")

        ctx.storage_state(path=str(state_file))
        print(f"\n✅ Successfully saved state for profile '{profile}' to: {state_file}\n")

    finally:
        browser.close()

def main(profile_arg: str | None, force: bool):
    """Main entrypoint for the bootstrap script."""
    profile = (profile_arg or get_last_profile()).lower().strip()
    (AUTH_DIR / ".last_profile").write_text(profile, encoding="utf-8")
    state_file = AUTH_DIR / f"{profile}.json"

    # Pre-check: Don't re-bootstrap if the state is already valid, unless forced.
    if not force and state_file.exists():
        print(f"[bootstrap] Found existing state for '{profile}'. Verifying...")
        is_valid = check_state_validity(profile, headed=False) == 0
        if is_valid:
            print(f"[bootstrap] ✅ Existing state is valid. Nothing to do.")
            print(f"[bootstrap] (Use --force to re-authenticate anyway)")
            return

    # Cleanup: Delete any old, potentially invalid state file before creating a new one.
    if state_file.exists():
        print(f"[bootstrap] Deleting old/invalid state file: {state_file.name}")
        state_file.unlink()

    with sync_playwright() as p:
        run_login_flow(p, profile, state_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstrap Avito auth state for a test profile.")
    parser.add_argument(
        "--profile",
        default=None,
        help="The profile to bootstrap (e.g., 'profile1'). If not provided, uses last one."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-authentication even if a valid state file exists."
    )
    args = parser.parse_args()
    main(args.profile, args.force)
