from datetime import date
from decimal import Decimal
import logging

from portfolio_tracker import database
from portfolio_tracker.errors import (
    InsufficientSharesError,
    InvalidAmountError,
    NoPortfolioSelectedError,
)
from portfolio_tracker.models.transaction import Transaction
from portfolio_tracker.services import (
    account_service,
    asset_service,
    holding_service,
    portfolio_service,
)
from portfolio_tracker.storage import transaction_store

logger = logging.getLogger(__name__)


def require_positive(label, value):
    if value <= Decimal("0"):
        raise InvalidAmountError(f"{label} must be greater than zero (got {value})")


def buy(portfolio_name, ticker, quantity, price_per_share):
    if portfolio_name is None:
        raise NoPortfolioSelectedError("No portfolio is currently selected")
    # One transaction for the whole trade: the debit and the trade record succeed or fail together.
    with database.transaction() as session:
        portfolio = portfolio_service.find_portfolio(session, portfolio_name)
        asset = asset_service.find_asset(session, ticker)
        require_positive("Quantity", quantity)
        require_positive("Price per share", price_per_share)

        rounded_qty = round(quantity, 4)
        rounded_price = round(price_per_share, 4)
        account_service.debit(session, rounded_qty * rounded_price)
        trade = Transaction(
            portfolio=portfolio,
            asset=asset,
            side="buy",
            quantity=rounded_qty,
            price_per_share=rounded_price,
            trade_date=date.today(),
        )
        transaction_store.add_transaction(session, trade)
    logger.info(
        "Bought %s %s at %.2f in %s",
        rounded_qty,
        asset.ticker,
        rounded_price,
        portfolio.name,
    )
    return trade


def sell(portfolio_name, ticker, quantity, price_per_share):
    if portfolio_name is None:
        raise NoPortfolioSelectedError("No portfolio is currently selected")
    with database.transaction() as session:
        portfolio = portfolio_service.find_portfolio(session, portfolio_name)
        asset = asset_service.find_asset(session, ticker)
        require_positive("Quantity", quantity)
        if price_per_share < Decimal("0"):
            raise InvalidAmountError(
                f"Price per share must be zero or more (got {price_per_share})"
            )

        rounded_qty = round(quantity, 4)
        rounded_price = round(price_per_share, 4)
        held = holding_service.get_quantity_held(session, portfolio, asset.ticker)
        if rounded_qty > held:
            raise InsufficientSharesError(
                f"Cannot sell {rounded_qty} {asset.ticker}; only {held} held in '{portfolio.name}'"
            )

        account_service.credit(session, rounded_qty * rounded_price)
        trade = Transaction(
            portfolio=portfolio,
            asset=asset,
            side="sell",
            quantity=rounded_qty,
            price_per_share=rounded_price,
            trade_date=date.today(),
        )
        transaction_store.add_transaction(session, trade)
    logger.info(
        "Sold %s %s at %.2f in %s",
        rounded_qty,
        asset.ticker,
        rounded_price,
        portfolio.name,
    )
    return trade
