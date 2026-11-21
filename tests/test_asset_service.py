import pytest

from portfolio_tracker.errors import DuplicateError, InvalidInputError
from portfolio_tracker.services import asset_service


def test_added_asset_appears_in_asset_list(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")

    [asset] = asset_service.list_assets()

    assert asset.ticker == "AAPL"
    assert asset.name == "Apple Inc."


def test_asset_ticker_is_stored_in_uppercase(empty_db):
    asset_service.add_asset("aapl", "Apple Inc.")

    [asset] = asset_service.list_assets()

    assert asset.ticker == "AAPL"


def test_asset_tickers_are_unique(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")

    with pytest.raises(DuplicateError):
        asset_service.add_asset("AAPL", "Another Apple")

    [asset] = asset_service.list_assets()
    assert asset.name == "Apple Inc."


def test_duplicate_ticker_in_lowercase_is_refused(empty_db):
    asset_service.add_asset("AAPL", "Apple Inc.")

    with pytest.raises(DuplicateError):
        asset_service.add_asset("aapl", "Another Apple")

    assert len(asset_service.list_assets()) == 1


def test_empty_ticker_is_refused(empty_db):
    with pytest.raises(InvalidInputError):
        asset_service.add_asset("   ", "Apple Inc.")

    assert asset_service.list_assets() == []


def test_empty_asset_name_is_refused(empty_db):
    with pytest.raises(InvalidInputError):
        asset_service.add_asset("AAPL", "   ")

    assert asset_service.list_assets() == []
