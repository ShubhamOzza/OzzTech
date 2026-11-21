import logging

from portfolio_tracker.errors import InvalidAmountError
from portfolio_tracker.services import asset_service

logger = logging.getLogger(__name__)

prices = {}


def set_price(ticker, price):
    asset = asset_service.find_asset(ticker)
    if price < 0:
        raise InvalidAmountError(f"Price must be zero or more (got {price})")
    prices[asset.ticker] = price
    logger.info("Set current price of %s to %.2f", asset.ticker, price)


def get_price(ticker):
    clean_ticker = ticker.strip().upper()
    return prices.get(clean_ticker)
