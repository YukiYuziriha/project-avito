# pages/home_page.py
from __future__ import annotations

import os
from typing import List
from playwright.sync_api import Page, Locator

# Fix: strip trailing whitespace from BASE_URL
BASE_URL = os.getenv("AVITO_BASE_URL", "https://www.avito.ru").strip()


class HomePage:
    """Avito homepage: locators + read-only actions (no assertions)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        # Stable locators from live DOM (per data-marker)
        self._search_input: Locator = page.locator(
            '[data-marker="search-form/suggest/input"]'
        )
        self._search_button: Locator = page.locator(
            '[data-marker="search-form/submit-button"]'
        )
        # CORRECTED: wait for at least one ad title to appear (user sees this)
        self._first_ad_title: Locator = page.locator('[data-marker="item-title"]').first
        self._ad_title_locator: Locator = page.locator('[data-marker="item-title"]')

    def navigate(self) -> HomePage:
        """Open Avito homepage and wait for initial render."""
        self.page.goto(BASE_URL, wait_until="domcontentloaded")
        self.page.wait_for_load_state("domcontentloaded")  # wait for initial render
        return self

    def search(self, query: str) -> HomePage:
        """Fill search input and click submit button."""
        self._search_input.fill(query)
        self._search_button.click()
        return self

    def wait_for_results(self, timeout: float = 15_000) -> HomePage:
        """Wait until at least one ad title is visible (user signal that results loaded)."""
        self._first_ad_title.wait_for(state="visible", timeout=timeout)
        return self

    def get_visible_ad_titles(self, max_count: int = 10) -> List[str]:
        """Return up to `max_count` visible ad titles (read-only, no interaction)."""
        titles = self._ad_title_locator.all_text_contents()
        return titles[:max_count]
