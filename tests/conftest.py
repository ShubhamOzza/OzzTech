from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from portfolio_tracker import database

# Imported so create_all() knows every table, as in main.py.
from portfolio_tracker.models import account, asset, portfolio, transaction  # noqa: F401
from portfolio_tracker.services import account_service, asset_service, portfolio_service
from portfolio_tracker.storage import portfolio_store, price_store


@pytest.fixture
def empty_db(monkeypatch):
    """Point the app at a brand-new, empty database for the length of one test."""
    engine = create_engine("sqlite://", poolclass=StaticPool)
    database.Base.metadata.create_all(engine)
    # The mock: for this test, "connect to the database" returns the in-memory one.
    monkeypatch.setattr(database, "get_engine", lambda: engine)
    monkeypatch.setattr(price_store, "current_prices", {})  # prices are stored in memory: start empty too
    monkeypatch.setattr(portfolio_store, "selection", {"name": None})
    yield  # the test runs here
    engine.dispose()  # monkeypatch puts the real get_engine back on its own


@pytest.fixture
def funded_portfolio(empty_db):
    """A typical starting point: $1,000 in cash, one portfolio, one asset."""
    account_service.deposit(Decimal("1000"))
    portfolio_service.create_portfolio("Tech growth", "Large-cap tech")
    asset_service.add_asset("AAPL", "Apple Inc.")
    return "Tech growth"
