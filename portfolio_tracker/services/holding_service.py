from portfolio_tracker.models.holding import Holding
from portfolio_tracker.services import portfolio_service, price_service, transaction_service


def _calculate_positions(portfolio):
    positions = {}
    realized_gain = 0.0

    for trade in transaction_service.get_transactions(portfolio):
        ticker = trade.asset.ticker
        if trade.side == "buy":
            if ticker not in positions or positions[ticker]["quantity"] == 0:
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
        if pos["quantity"] > 0:
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


def get_holdings(portfolio_name):
    portfolio = portfolio_service.find_portfolio(portfolio_name)
    holdings, _ = _calculate_positions(portfolio)
    return holdings


def get_quantity_held(portfolio_name, ticker):
    for holding in get_holdings(portfolio_name):
        if holding.asset.ticker == ticker:
            return holding.quantity
    return 0


def get_portfolio_summary(portfolio_name):
    portfolio = portfolio_service.find_portfolio(portfolio_name)
    holdings, realized_gain = _calculate_positions(portfolio)

    total_market_value = 0.0
    total_unrealized_gain = 0.0
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
