# tests/smoke/test_login_factory.py
import os


def test_login_factory_smoke(login_factory):
    page = login_factory("profile1")
    base_url = os.getenv("AVITO_BASE_URL", "https://www.avito.ru")
    page.goto(f"{base_url}/profile")

    assert "profile" in page.url.lower()
    assert page.locator("input[name='login']").count() == 0
    assert page.get_by_text("Мой профиль").is_visible() or (
        "profile" in page.url.lower() and "login" not in page.url.lower()
    )
