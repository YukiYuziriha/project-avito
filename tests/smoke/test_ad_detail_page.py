# tests/smoke/test_ad_detail_page.py
from pages.home_page import HomePage
from pages.ad_detail_page import AdDetailPage


def test_can_view_ad_detail(login_factory):
    """
    P0 smoke test: authenticated user can search, click an ad (opens in new tab),
    and view ad detail with title and price.
    Uses cached session state — no login-page interaction.
    """
    page = login_factory("profile1")
    home = HomePage(page)
    home.navigate().search("iphone").wait_for_results()

    # Click first ad — it opens in a new tab (popup)
    with page.expect_popup() as popup_info:
        home._ad_title_locator.first.click()

    new_page = popup_info.value
    new_page.wait_for_load_state("domcontentloaded")

    # Use the new page for ad detail
    ad_detail = AdDetailPage(new_page)
    ad_detail.wait_for_loaded()

    title = ad_detail.get_title()
    price = ad_detail.get_price()

    assert len(title) > 0, "Ad title should not be empty"
    assert len(price) > 0, "Ad price should not be empty"