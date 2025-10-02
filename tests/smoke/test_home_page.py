# tests/smoke/test_home_page.py
from pages.home_page import HomePage


def test_home_page_search_smoke(login_factory):
    """
    P0 smoke test: authenticated user can search and see results.
    Uses cached session; no login page interaction.
    Waits for first ad title to appear (user-centric signal).
    """
    page = login_factory("profile1")
    home = HomePage(page)

    home.navigate().search("iphone").wait_for_results()

    titles = home.get_visible_ad_titles()
    assert len(titles) > 0, "Expected at least one ad to appear after search"
