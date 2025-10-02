# pages/login_page.py
from __future__ import annotations

import os
from playwright.sync_api import Page, Locator

BASE_URL = os.getenv("AVITO_BASE_URL", "https://www.avito.ru")


class LoginPage:
    """Avito login screen: locators + actions (no assertions)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        # Locators — prefer stable attrs / roles; adjust to real DOM if needed.
        self._username_input: Locator = page.locator('[name="login"]')
        self._password_input: Locator = page.locator('[name="password"]')
        self._submit_btn: Locator = page.get_by_role("button", name="Войти")
        # Avito widely uses data-marker; include a tolerant selector.
        self._error: Locator = page.locator(
            '[data-marker="login-form/error"], [data-marker="auth/error"]'
        )

    # -------- actions (no assertions) --------
    def navigate(self) -> None:
        """Open login page and wait until the form is ready."""
        self.page.goto(f"{BASE_URL}/profile/login", wait_until="domcontentloaded")
        self._username_input.wait_for(state="visible")

    def fill_username(self, username: str) -> None:
        self._username_input.fill(username)

    def fill_password(self, password: str) -> None:
        self._password_input.fill(password)

    def submit(self) -> None:
        self._submit_btn.click()

    def login(self, username: str, password: str) -> None:
        """Convenience: fill both fields and click submit."""
        self.fill_username(username)
        self.fill_password(password)
        self.submit()

    # -------- surfaced locators/data for tests --------
    @property
    def error_locator(self) -> Locator:
        """Expose the error locator so tests can assert on it."""
        return self._error

    def error_text_now(self) -> str | None:
        """Return current error text if visible, else None (no assertions)."""
        if self._error.is_visible():
            return self._error.inner_text()
        return None
