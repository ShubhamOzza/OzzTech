from decimal import Decimal
import logging

from portfolio_tracker import database
from portfolio_tracker.errors import InvalidAmountError
from portfolio_tracker.services import asset_service
from portfolio_tracker.storage import price_store

logger = logging.getLogger(__name__)


def set_price(ticker, price):
    if price < Decimal("0"):
        raise InvalidAmountError(f"Price must be zero or more (got {price})")
    with database.transaction() as session:
        asset = asset_service.find_asset(session, ticker)
    rounded = round(price, 4)
    price_store.set_price(asset.ticker, rounded)
    logger.info("Set current price of %s to %.2f", asset.ticker, rounded)


def get_price(ticker):
    clean_ticker = ticker.strip().upper()
    return price_store.get_price(clean_ticker)
