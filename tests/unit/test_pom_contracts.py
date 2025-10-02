# tests/unit/test_pom_contracts.py
from unittest.mock import Mock
from pages.home_page import HomePage
from pages.ad_detail_page import AdDetailPage

def test_home_page_instantiates():
    mock_page = Mock()
    home = HomePage(mock_page)
    assert home is not None

def test_ad_detail_page_instantiates():
    mock_page = Mock()
    ad = AdDetailPage(mock_page)
    assert ad is not None