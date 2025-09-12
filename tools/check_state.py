# tools/check_state.py
from pathlib import Path
import argparse
import os
import time
from dotenv import load_dotenv, find_dotenv
from playwright.sync_api import sync_playwright, Page, Playwright, Browser
from filelock import FileLock, Timeout

# --- Setup -------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(find_dotenv())

AUTH_DIR = ROOT / ".auth"
ART_DIR = ROOT / "artifacts"
ART_DIR.mkdir(exist_ok=True)
TRACE_DIR = ART_DIR / "traces"
TRACE_DIR.mkdir(exist_ok=True)


# --- Helpers -----------------------------------------------------------------
def is_logged_in(page: Page) -> bool:
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
    return "profile" in url and "login" not in url


def save_artifacts(page: Page, profile: str, reason: str):
    """Saves screenshot, HTML, and trace file for debugging."""
    ts = int(time.time())
    base_name = f"state_check_{profile}_{reason}_{ts}"
    try:
        # Save Screenshot and HTML
        png_path = ART_DIR / f"{base_name}.png"
        page.screenshot(path=str(png_path), full_page=True)
        html_path = ART_DIR / f"{base_name}.html"
        html_path.write_text(page.content(), encoding="utf-8")
        print(f"[state] ❌ Saved artifacts: {png_path.name}, {html_path.name}")
    except Exception as e:
        print(f"[state] ❌ Could not save screenshot/HTML artifacts: {e}")


# --- Main Function -----------------------------------------------------------
def check(profile: str, headed: bool) -> int:
    """
    (Process-safe) Checks the validity of a saved auth state.
    Returns exit code: 0=valid, 1=invalid, 2=missing, 3=timeout/lock_error.
    """
    state_file = AUTH_DIR / f"{profile}.json"
    if not state_file.exists():
        print(f"[state] ❌ Missing state file for profile '{profile}': {state_file}")
        return 2

    lock_file = state_file.with_suffix(".json.lock")
    try:
        # Use a file lock to prevent multiple CI jobs checking at the same time
        with FileLock(str(lock_file), timeout=60):
            with sync_playwright() as p:
                return run_check_with_browser(p, profile, state_file, headed)
    except Timeout:
        print(f"[state] ❌ Timeout: Could not acquire lock '{lock_file.name}' within 60s.")
        return 3
    except Exception as e:
        print(f"[state] ❌ An unexpected error occurred: {e}")
        return 3

def run_check_with_browser(p: Playwright, profile: str, state_file: Path, headed: bool) -> int:
    """The core logic for browser interaction and validation."""
    browser = p.chromium.launch(headless=not headed)
    context = browser.new_context(storage_state=str(state_file))
    # Start tracing for better debugging artifacts
    trace_path = TRACE_DIR / f"trace_{profile}_{int(time.time())}.zip"
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    try:
        # Master timeout for the entire check
        page.set_default_timeout(20_000) # 20 seconds
        
        page.goto("https://www.avito.ru/profile")

        # Wait for the page to settle, up to 10 seconds
        page.wait_for_load_state('networkidle', timeout=10_000)

        if is_logged_in(page):
            print(f"[state] ✅ Valid state for profile '{profile}': {state_file}")
            context.tracing.stop() # No need to save trace on success
            return 0
        else:
            # If invalid, save all artifacts before returning
            context.tracing.stop(path=str(trace_path))
            print(f"[state] ❌ Invalid state. Saved Playwright Trace: {trace_path.name}")
            save_artifacts(page, profile, "invalid")
            return 1

    except Exception as e:
        print(f"[state] ❌ Check failed with an exception: {e}")
        context.tracing.stop(path=str(trace_path))
        print(f"[state] ❌ Saved Playwright Trace due to error: {trace_path.name}")
        save_artifacts(page, profile, "error")
        return 3
    finally:
        context.close()
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate a saved Avito auth state.")
    parser.add_argument(
        "--profile",
        default="profile1",
        help="The profile to check (e.g., 'profile1')."
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run the browser in headed mode to observe."
    )
    args = parser.parse_args()
    raise SystemExit(check(args.profile.lower().strip(), args.headed))