# tools/check_state.py
from pathlib import Path
import argparse, os, time
from dotenv import load_dotenv, find_dotenv
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(find_dotenv())

AUTH_DIR = ROOT / ".auth"
ART_DIR  = ROOT / "artifacts"
ART_DIR.mkdir(exist_ok=True)

def click_continue_if_needed(page):
    try:
        page.get_by_text("Продолжить", exact=True).first.click(timeout=1000)
    except Exception:
        pass

def logged_in(page) -> bool:
    url = page.url.lower()
    if "profile/login" in url:
        return False
    # login form present => not logged in
    if page.locator("input[name='login']").count() or page.locator("input[type='password']").count():
        return False
    # positive signal (text shown only when authorized)
    if page.locator("text=Мой профиль").count():
        return True
    # fallback: profile without /login
    return ("profile" in url) and ("login" not in url)

def check(role: str, headed: bool) -> int:
    state_file = AUTH_DIR / f"{role}.json"
    if not state_file.exists():
        print(f"[state] ❌ Missing state: {state_file}")
        return 2

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        ctx = browser.new_context(storage_state=str(state_file))
        page = ctx.new_page()
        try:
            page.goto("https://www.avito.ru/profile", timeout=60_000)
            deadline = time.time() + 10
            while time.time() < deadline and not logged_in(page):
                click_continue_if_needed(page)
                page.wait_for_timeout(500)

            if logged_in(page):
                print(f"[state] ✅ Valid: {state_file}")
                return 0

            # artifacts to see what's actually on screen
            ts = int(time.time())
            png = ART_DIR / f"state_check_{role}_{ts}.png"
            html = ART_DIR / f"state_check_{role}_{ts}.html"
            try:
                page.screenshot(path=str(png), full_page=True)
                html.write_text(page.content(), encoding="utf-8")
                print(f"[state] ❌ Not logged in. Saved artifacts/{png.name} and artifacts/{html.name}")
            except Exception as e:
                print(f"[state] ❌ Not logged in (artifact error: {e})")
            return 1
        finally:
            ctx.close()
            browser.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", default=os.getenv("AVITO_ROLE", "buyer"))
    ap.add_argument("--headed", action="store_true")
    args = ap.parse_args()
    raise SystemExit(check(args.role.lower().strip(), args.headed))
