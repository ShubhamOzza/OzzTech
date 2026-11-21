import logging

from portfolio_tracker.errors import DuplicateError, InvalidInputError, NotFoundError
from portfolio_tracker.models.asset import Asset

logger = logging.getLogger(__name__)

assets = {}


def add_asset(ticker, name):
    clean_ticker = ticker.strip().upper()
    clean_name = name.strip()
    if not clean_ticker:
        raise InvalidInputError("Ticker cannot be empty")
    if not clean_name:
        raise InvalidInputError("Asset name cannot be empty")
    if clean_ticker in assets:
        raise DuplicateError(f"Asset '{clean_ticker}' already exists")
    asset = Asset(clean_ticker, clean_name)
    assets[clean_ticker] = asset
    logger.info("Added asset %s (%s)", asset.ticker, asset.name)
    return asset


def find_asset(ticker):
    clean_ticker = ticker.strip().upper()
    try:
        return assets[clean_ticker]
    except KeyError:
        raise NotFoundError(f"No asset with ticker '{clean_ticker}'") from None


def list_assets():
    return list(assets.values())
