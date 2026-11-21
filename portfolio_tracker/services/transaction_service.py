import logging

from portfolio_tracker.errors import InsufficientSharesError, InvalidAmountError
from portfolio_tracker.models.transaction import Transaction
from portfolio_tracker.services import (
    account_service,
    asset_service,
    holding_service,
    portfolio_service,
)

logger = logging.getLogger(__name__)

transactions = []


def require_positive(label, value):
    if value <= 0:
        raise InvalidAmountError(f"{label} must be greater than zero (got {value})")


def buy(portfolio_name, ticker, quantity, price_per_share):
    portfolio = portfolio_service.find_portfolio(portfolio_name)
    asset = asset_service.find_asset(ticker)
    require_positive("Quantity", quantity)
    require_positive("Price per share", price_per_share)

    account_service.debit(quantity * price_per_share)
    trade = Transaction(portfolio, asset, "buy", quantity, price_per_share)
    transactions.append(trade)
    logger.info(
        "Bought %s %s at %.2f in %s",
        quantity,
        asset.ticker,
        price_per_share,
        portfolio.name,
    )
    return trade


def sell(portfolio_name, ticker, quantity, price_per_share):
    portfolio = portfolio_service.find_portfolio(portfolio_name)
    asset = asset_service.find_asset(ticker)
    require_positive("Quantity", quantity)
    if price_per_share < 0:
        raise InvalidAmountError(f"Price per share must be zero or more (got {price_per_share})")

    held = holding_service.get_quantity_held(portfolio.name, asset.ticker)
    if quantity > held:
        raise InsufficientSharesError(
            f"Cannot sell {quantity} {asset.ticker}; only {held} held in '{portfolio.name}'"
        )

    account_service.credit(quantity * price_per_share)
    trade = Transaction(portfolio, asset, "sell", quantity, price_per_share)
    transactions.append(trade)
    logger.info(
        "Sold %s %s at %.2f in %s",
        quantity,
        asset.ticker,
        price_per_share,
        portfolio.name,
    )
    return trade


def get_transactions(portfolio):
    result = []
    for trade in transactions:
        if trade.portfolio == portfolio:
            result.append(trade)
    return result


def clear_transactions(portfolio):
    remaining = []
    for trade in transactions:
        if trade.portfolio != portfolio:
            remaining.append(trade)
    transactions.clear()
    for trade in remaining:
        transactions.append(trade)
