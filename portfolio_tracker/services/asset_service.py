import logging

from portfolio_tracker import database
from portfolio_tracker.errors import DuplicateError, InvalidInputError, NotFoundError
from portfolio_tracker.models.asset import Asset
from portfolio_tracker.storage import asset_store

logger = logging.getLogger(__name__)


def add_asset(ticker, name):
    clean_ticker = ticker.strip().upper()
    clean_name = name.strip()
    if not clean_ticker:
        raise InvalidInputError("Ticker cannot be empty")
    if not clean_name:
        raise InvalidInputError("Asset name cannot be empty")
    with database.transaction() as session:
        if asset_store.get_asset(session, clean_ticker) is not None:
            raise DuplicateError(f"Asset '{clean_ticker}' already exists")
        asset = Asset(ticker=clean_ticker, name=clean_name)
        asset_store.add_asset(session, asset)
    logger.info("Added asset %s (%s)", asset.ticker, asset.name)
    return asset


def find_asset(session, ticker):
    clean_ticker = ticker.strip().upper()
    asset = asset_store.get_asset(session, clean_ticker)
    if asset is None:
        raise NotFoundError(f"No asset with ticker '{clean_ticker}'")
    return asset


def list_assets():
    with database.transaction() as session:
        return asset_store.get_all_assets(session)
