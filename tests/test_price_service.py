from decimal import Decimal

import pytest

from portfolio_tracker.errors import InvalidAmountError, NotFoundError
from portfolio_tracker.services import asset_service, price_service


def test_asset_starts_with_no_current_price(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")

    assert price_service.get_price("AAPL") is None


def test_setting_price_stores_current_price(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")

    price_service.set_price("aapl", Decimal("185.50"))

    assert price_service.get_price("AAPL") == Decimal("185.50")


def test_setting_zero_price_is_allowed(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")

    price_service.set_price("AAPL", Decimal("0"))

    assert price_service.get_price("AAPL") == Decimal("0")


def test_setting_negative_price_is_refused(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")

    with pytest.raises(InvalidAmountError):
        price_service.set_price("AAPL", Decimal("-0.01"))

    assert price_service.get_price("AAPL") is None


def test_setting_price_for_unknown_ticker_is_refused(empty_db):
    with pytest.raises(NotFoundError):
        price_service.set_price("MSFT", Decimal("300"))

    assert price_service.get_price("MSFT") is None
