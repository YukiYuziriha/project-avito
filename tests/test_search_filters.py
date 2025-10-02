# tests/test_search_filters.py
def test_buyer_search(login_factory):
    page = login_factory("buyer")  # Logs as buyer, reuses state if available
    page.goto("https://www.avito.ru")
    # Perform search actions
