# pages/ad_detail_page.py
from __future__ import annotations

from typing import Optional
from playwright.sync_api import Page, Locator


class AdDetailPage:
    """Avito ad detail page: read-only actions and data extraction (no assertions)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        # Scoped to main content area to avoid duplicates in sticky footer / related ads
        self._title_locator: Locator = page.locator('[data-marker="item-view/title-info"]')
        self._price_locator: Locator = page.locator(
            '.js-item-view-title-info [data-marker="item-view/item-price"]'
        )
        self._location_locator: Locator = page.locator('[itemprop="address"]')

    def wait_for_loaded(self, timeout: float = 15_000) -> AdDetailPage:
        """Wait until core ad elements are visible — user signal of load."""
        self._title_locator.wait_for(state="visible", timeout=timeout)
        self._price_locator.wait_for(state="visible", timeout=timeout)
        return self

    def get_title(self) -> str:
        """Return ad title text (assumes element is visible due to wait_for_loaded)."""
        title = self._title_locator.text_content()
        return title.strip() if title else ""

    def get_price(self) -> str:
        """Return ad price text (e.g., '12 990 ₽')."""
        price = self._price_locator.text_content()
        return price.strip() if price else ""

    def get_location(self) -> Optional[str]:
        """Return ad location if present and visible."""
        if self._location_locator.is_visible():
            loc = self._location_locator.text_content()
            return loc.strip() if loc else None
        return None