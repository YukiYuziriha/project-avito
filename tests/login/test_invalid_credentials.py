# tests/login/test_invalid_credentials.py
import os
import pytest
from playwright.sync_api import expect
from pages.login_page import LoginPage

pytestmark = pytest.mark.auth # marked for sanity

def test_invalid_login(page):
    lp = LoginPage(page)
    lp.navigate()

    lp.login("fake_user@example.com", "wrong-password")

    expect(lp.error_locator).to_be_visible()
    expect(lp.error_locator).to_contain_text("Неверный пароль")

