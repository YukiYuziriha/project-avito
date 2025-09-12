# tests/smoke/test_login_factory.py
def test_login_factory_smoke(login_factory):
    page = login_factory("profile1")
    page.goto("https://www.avito.ru/profile")
    assert "profile" in page.url.lower()
    assert not page.locator("input[name='login']").count()
    assert page.get_by_text("Мой профиль").count() or ("profile" in page.url.lower() and "login" not in page.url.lower())
