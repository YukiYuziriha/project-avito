# tools/bootstrap_auth.py
from pathlib import Path
import os, sys, time, argparse
from dotenv import load_dotenv, find_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(find_dotenv())

AUTH_DIR = ROOT / ".auth"
AUTH_DIR.mkdir(exist_ok=True)

def infer_role(default="buyer") -> str:
    # 1) remember last role if present
    hint_file = AUTH_DIR / ".last_role"
    if hint_file.exists():
        r = hint_file.read_text(encoding="utf-8").strip().lower()
        if r:
            return r
    # 2) infer from .env keys
    if os.getenv("AVITO_BUYER_USERNAME") or os.getenv("AVITO_BUYER_PASSWORD"):
        return "buyer"
    if os.getenv("AVITO_SELLER_USERNAME") or os.getenv("AVITO_SELLER_PASSWORD"):
        return "seller"
    # 3) default
    return default

def resolve_creds(role: str):
    role_up = role.upper()
    user = os.getenv(f"AVITO_{role_up}_USERNAME") or os.getenv("AVITO_USERNAME")
    pwd  = os.getenv(f"AVITO_{role_up}_PASSWORD") or os.getenv("AVITO_PASSWORD")
    assert user and pwd, (
        f"Missing creds in .env. Provide AVITO_{role_up}_USERNAME/AVITO_{role_up}_PASSWORD "
        f"or generic AVITO_USERNAME/AVITO_PASSWORD at repo root."
    )
    return user, pwd

def is_logged_in(page) -> bool:
    url = page.url.lower()
    if "profile/login" in url:
        return False
    # login form => not logged in
    if page.locator("input[name='login']").count() or page.locator("input[type='password']").count():
        return False
    # positive signal
    if page.locator("text=Мой профиль").count():
        return True
    return ("profile" in url) and ("login" not in url)

def click_continue_if_needed(page):
    try:
        page.get_by_text("Продолжить", exact=True).first.click(timeout=1000)
    except Exception:
        pass

def main(role_arg: str | None):
    role = (role_arg or infer_role()).lower().strip()
    (AUTH_DIR / ".last_role").write_text(role, encoding="utf-8")
    user, pwd = resolve_creds(role)
    state_file = AUTH_DIR / f"{role}.json"

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        ctx = browser.new_context()
        page = ctx.new_page()

        # 1) open login & submit once
        page.goto("https://www.avito.ru/profile/login", timeout=60_000)
        try:
            page.fill('input[name="login"]', user, timeout=10_000)
            page.fill('input[name="password"]', pwd,  timeout=10_000)
        except Exception:
            page.fill("input[type='text']", user, timeout=10_000)
            page.fill("input[type='password']", pwd, timeout=10_000)
        page.click('button[type="submit"]', timeout=10_000)
        click_continue_if_needed(page)

        # 2) HUMAN step: explicit ENTER to save (with auto-wait fallback if no TTY)
        if sys.stdin.isatty():
            print(
                f"\n[bootstrap:{role}] Solve CAPTCHA + enter the SMS in the **browser window**."
                f"\n[bootstrap:{role}] When you are REALLY logged in (profile visible), press ENTER here."
                f"\n[bootstrap:{role}] If it says 'not logged in', keep going in the browser and press ENTER again."
            )
            while True:
                try:
                    input("\n[bootstrap] Press ENTER to verify login… ")
                except EOFError:
                    # unexpected non-tty -> fallback to auto loop
                    break
                try:
                    page.goto("https://www.avito.ru/profile", timeout=10_000)
                except PWTimeout:
                    pass
                click_continue_if_needed(page)
                if is_logged_in(page):
                    break
                print("[bootstrap] Not logged in yet. Continue in the browser and press ENTER again.")
        else:
            print("\n[bootstrap] No TTY; auto-waiting up to 10 minutes for login…\n")
            deadline = time.time() + 600
            last_err = None
            while time.time() < deadline:
                click_continue_if_needed(page)
                if is_logged_in(page):
                    break
                if int(time.time()) % 15 == 0:
                    try:
                        page.goto("https://www.avito.ru/profile", timeout=5_000)
                    except Exception as e:
                        last_err = e
                page.wait_for_timeout(1000)
            if not is_logged_in(page):
                raise TimeoutError(f"Login not detected within 10 minutes. Last error: {last_err}")

        # 3) final verify + save
        try:
            page.goto("https://www.avito.ru/profile", timeout=10_000)
        except PWTimeout:
            pass
        click_continue_if_needed(page)
        if not is_logged_in(page):
            raise RuntimeError("[bootstrap] Still not logged in — refusing to save a bad state.")

        ctx.storage_state(path=str(state_file))
        print(f"\n✅ Saved state for role '{role}': {state_file}\n")
        browser.close()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Bootstrap Avito auth storage state")
    ap.add_argument("--role", choices=["buyer","seller"], default=None, help="optional; default inferred")
    args = ap.parse_args()
    main(args.role)
