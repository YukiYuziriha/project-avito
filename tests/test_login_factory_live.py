from pathlib import Path
import os

def test_login_factory_live(login_factory):
    # First login: should perform UI login and save storage state
    page = login_factory("buyer", reuse_state=True)  # stores .auth/<username>.json
    try:
        # You already wait in _do_login; this is an extra belt-and-braces check
        page.wait_for_selector("text=Мой профиль", timeout=15000)
        assert "profile" in page.url.lower()

        # Verify storage state file exists (reuse will be instant next run)
        root = Path(__file__).resolve().parent.parent  # repo root
        uname = os.getenv("AVITO_BUYER_USERNAME") or os.getenv("AVITO_USERNAME")
        assert uname, "No username found in env (AVITO_BUYER_USERNAME or AVITO_USERNAME)."
        state_file = root / ".auth" / f"{uname}.json"
        assert state_file.exists(), f"Expected {state_file} to be created."
    finally:
        page.context.close()
