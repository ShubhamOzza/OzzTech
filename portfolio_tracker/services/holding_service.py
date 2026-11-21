from decimal import Decimal

from portfolio_tracker import database
from portfolio_tracker.models.holding import Holding
from portfolio_tracker.services import portfolio_service, price_service
from portfolio_tracker.storage import transaction_store


def calculate_portfolio_positions(session, portfolio):
    positions = {}
    realized_gain = Decimal("0")

    for trade in transaction_store.get_transactions(session, portfolio):
        ticker = trade.asset.ticker
        if trade.side == "buy":
            if ticker not in positions or positions[ticker]["quantity"] == Decimal("0"):
                positions[ticker] = {
                    "asset": trade.asset,
                    "quantity": trade.quantity,
                    "average_cost": trade.price_per_share,
                }
            else:
                pos = positions[ticker]
                total_paid = (pos["quantity"] * pos["average_cost"]) + (
                    trade.quantity * trade.price_per_share
                )
                new_quantity = pos["quantity"] + trade.quantity
                pos["quantity"] = new_quantity
                pos["average_cost"] = total_paid / new_quantity
        elif trade.side == "sell":
            pos = positions[ticker]
            realized_gain += (trade.price_per_share - pos["average_cost"]) * trade.quantity
            pos["quantity"] -= trade.quantity

    holdings = []
    for ticker, pos in positions.items():
        if pos["quantity"] > Decimal("0"):
            current_price = price_service.get_price(ticker)
            holdings.append(
                Holding(
                    pos["asset"],
                    pos["quantity"],
                    pos["average_cost"],
                    current_price,
                )
            )
    return holdings, realized_gain


def get_quantity_held(session, portfolio, ticker):
    holdings, _ = calculate_portfolio_positions(session, portfolio)
    for holding in holdings:
        if holding.asset.ticker == ticker:
            return holding.quantity
    return Decimal("0")


def get_holdings(portfolio_name):
    with database.transaction() as session:
        portfolio = portfolio_service.find_portfolio(session, portfolio_name)
        holdings, _ = calculate_portfolio_positions(session, portfolio)
        return holdings


def get_portfolio_summary(portfolio_name):
    with database.transaction() as session:
        portfolio = portfolio_service.find_portfolio(session, portfolio_name)
        holdings, realized_gain = calculate_portfolio_positions(session, portfolio)

    total_market_value = Decimal("0")
    total_unrealized_gain = Decimal("0")
    for holding in holdings:
        if holding.market_value is not None:
            total_market_value += holding.market_value
            total_unrealized_gain += holding.unrealized_gain

    return {
        "portfolio": portfolio,
        "holdings": holdings,
        "total_market_value": total_market_value,
        "total_unrealized_gain": total_unrealized_gain,
        "realized_gain": realized_gain,
    }
