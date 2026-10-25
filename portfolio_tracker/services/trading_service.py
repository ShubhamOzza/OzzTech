import logging
import math

from portfolio_tracker.domain.portfolio import Portfolio, Position, Trade
from portfolio_tracker.errors import (
    InsufficientSharesError,
    InvalidPriceError,
    InvalidQuantityError,
)
from portfolio_tracker.services.asset_service import AssetService
from portfolio_tracker.services.cash_service import CashService
from portfolio_tracker.services.portfolio_service import PortfolioService

logger = logging.getLogger(__name__)


def _check_whole_quantity(quantity: int) -> None:
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        raise InvalidQuantityError("Quantity must be a whole number greater than zero.")


class TradingService:
    def __init__(
        self,
        asset_service: AssetService,
        cash_service: CashService,
        portfolio_service: PortfolioService,
    ):
        self._asset_service = asset_service
        self._cash_service = cash_service
        self._portfolio_service = portfolio_service

    def buy_asset(self, ticker: str, quantity: int, price: float) -> Trade:
        portfolio = self._portfolio_service.require_selected_portfolio()
        asset = self._asset_service.get_asset(ticker)
        _check_whole_quantity(quantity)

        if math.isnan(price) or math.isinf(price) or price <= 0:
            raise InvalidPriceError("Buy price per share must be greater than zero.")

        total_cost = round(quantity * price, 8)
        self._cash_service.deduct_cash(total_cost)
        self._update_position_after_buy(portfolio, asset.ticker, quantity, price)

        trade = Trade("BUY", asset.ticker, quantity, price, total_cost)
        portfolio.trades.append(trade)
        logger.info(
            "Bought %d shares of %s at %.2f in portfolio '%s'",
            quantity,
            asset.ticker,
            price,
            portfolio.name,
        )
        return trade

    def sell_asset(self, ticker: str, quantity: int, price: float) -> Trade:
        portfolio = self._portfolio_service.require_selected_portfolio()
        asset = self._asset_service.get_asset(ticker)
        _check_whole_quantity(quantity)

        if math.isnan(price) or math.isinf(price) or price < 0:
            raise InvalidPriceError("Sell price per share must be zero or more.")

        position = self._get_held_position(portfolio, asset.ticker, quantity)
        proceeds = round(quantity * price, 8)
        realized_gain = (price - position.average_cost) * quantity

        self._cash_service.add_cash(proceeds)
        self._update_position_after_sell(portfolio, position, quantity)
        portfolio.realized_gain += realized_gain

        trade = Trade(
            "SELL",
            asset.ticker,
            quantity,
            price,
            proceeds,
            realized_gain=realized_gain,
        )
        portfolio.trades.append(trade)
        logger.info(
            "Sold %d shares of %s at %.2f in portfolio '%s' (realized gain: %.2f)",
            quantity,
            asset.ticker,
            price,
            portfolio.name,
            realized_gain,
        )
        return trade

    def _update_position_after_buy(
        self,
        portfolio: Portfolio,
        ticker: str,
        quantity: int,
        price: float,
    ) -> None:
        if ticker in portfolio.positions:
            existing = portfolio.positions[ticker]
            old_cost = existing.quantity * existing.average_cost
            new_quantity = existing.quantity + quantity
            existing.average_cost = (old_cost + (quantity * price)) / new_quantity
            existing.quantity = new_quantity
        else:
            portfolio.positions[ticker] = Position(ticker, quantity, price)

    def _get_held_position(
        self,
        portfolio: Portfolio,
        ticker: str,
        requested_quantity: int,
    ) -> Position:
        try:
            position = portfolio.positions[ticker]
        except KeyError as err:
            raise InsufficientSharesError(
                ticker,
                requested_quantity,
                0,
                portfolio.name,
            ) from err

        if requested_quantity > position.quantity:
            raise InsufficientSharesError(
                ticker,
                requested_quantity,
                position.quantity,
                portfolio.name,
            )
        return position

    def _update_position_after_sell(
        self,
        portfolio: Portfolio,
        position: Position,
        sold_quantity: int,
    ) -> None:
        remaining = position.quantity - sold_quantity
        if remaining == 0:
            # Remove closed position from active holdings; realized gain stays on portfolio
            del portfolio.positions[position.ticker]
        else:
            position.quantity = remaining
