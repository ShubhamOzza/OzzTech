import logging

from portfolio_tracker.domain.portfolio import Portfolio, Position
from portfolio_tracker.errors import (
    DuplicatePortfolioError,
    InvalidNameError,
    NoPortfolioSelectedError,
    PortfolioNotEmptyError,
    PortfolioNotFoundError,
)
from portfolio_tracker.services.asset_service import AssetService
from portfolio_tracker.services.pricing_service import PricingService

logger = logging.getLogger(__name__)


class PortfolioService:
    def __init__(self, asset_service: AssetService, pricing_service: PricingService):
        self._asset_service = asset_service
        self._pricing_service = pricing_service
        self._portfolios: dict[str, Portfolio] = {}
        self._selected_key: str | None = None

    def create_portfolio(self, name: str, strategy: str) -> Portfolio:
        clean_name = name.strip()
        clean_strategy = strategy.strip()
        if not clean_name:
            raise InvalidNameError("Portfolio name cannot be empty.")
        if not clean_strategy:
            raise InvalidNameError("Investment strategy cannot be empty.")

        key = clean_name.lower()
        if key in self._portfolios:
            raise DuplicatePortfolioError(clean_name)

        portfolio = Portfolio(clean_name, clean_strategy)
        self._portfolios[key] = portfolio
        logger.info("Created portfolio '%s' (%s)", portfolio.name, portfolio.strategy)
        return portfolio

    def list_portfolios(self) -> list[dict]:
        result = []
        for key, portfolio in self._portfolios.items():
            result.append(
                {
                    "name": portfolio.name,
                    "strategy": portfolio.strategy,
                    "is_selected": key == self._selected_key,
                }
            )
        return result

    def get_selected_portfolio(self) -> Portfolio | None:
        if self._selected_key is None:
            return None
        return self._portfolios.get(self._selected_key)

    def require_selected_portfolio(self) -> Portfolio:
        portfolio = self.get_selected_portfolio()
        if portfolio is None:
            raise NoPortfolioSelectedError()
        return portfolio

    def select_portfolio(self, name: str) -> Portfolio:
        key, portfolio = self._lookup_portfolio(name)
        self._selected_key = key
        logger.info("Selected portfolio '%s'", portfolio.name)
        return portfolio

    def delete_portfolio(self, name: str) -> tuple[Portfolio, bool]:
        key, portfolio = self._lookup_portfolio(name)

        held_tickers = sorted(
            ticker for ticker, pos in portfolio.positions.items() if pos.quantity > 0
        )
        if held_tickers:
            raise PortfolioNotEmptyError(portfolio.name, held_tickers)

        was_selected = self._selected_key == key
        del self._portfolios[key]
        if was_selected:
            self._selected_key = None

        logger.info(
            "Deleted portfolio '%s' (was_selected=%s)",
            portfolio.name,
            was_selected,
        )
        return portfolio, was_selected

    def get_selected_portfolio_summary(self) -> dict:
        portfolio = self.require_selected_portfolio()
        position_rows = []
        total_market_value = 0.0
        total_unrealized_gain = 0.0
        unpriced_tickers = []

        for ticker in sorted(portfolio.positions):
            position = portfolio.positions[ticker]
            if position.quantity <= 0:
                continue

            row = self._build_position_row(position)
            position_rows.append(row)

            if row["market_value"] is not None and row["unrealized_gain"] is not None:
                total_market_value += row["market_value"]
                total_unrealized_gain += row["unrealized_gain"]
            else:
                unpriced_tickers.append(ticker)

        return {
            "name": portfolio.name,
            "strategy": portfolio.strategy,
            "positions": position_rows,
            "total_market_value": total_market_value,
            "total_unrealized_gain": total_unrealized_gain,
            "total_realized_gain": portfolio.realized_gain,
            "unpriced_tickers": unpriced_tickers,
        }

    def _build_position_row(self, position: Position) -> dict:
        asset = self._asset_service.get_asset(position.ticker)
        current_price = self._pricing_service.get_price(position.ticker)

        if current_price is None:
            market_value = None
            unrealized_gain = None
        else:
            market_value = current_price * position.quantity
            unrealized_gain = (current_price - position.average_cost) * position.quantity

        return {
            "ticker": position.ticker,
            "name": asset.name,
            "quantity": position.quantity,
            "average_cost": position.average_cost,
            "current_price": current_price,
            "market_value": market_value,
            "unrealized_gain": unrealized_gain,
        }

    def _lookup_portfolio(self, name: str) -> tuple[str, Portfolio]:
        clean_name = name.strip()
        if not clean_name:
            raise InvalidNameError("Portfolio name cannot be empty.")

        key = clean_name.lower()
        try:
            return key, self._portfolios[key]
        except KeyError as err:
            raise PortfolioNotFoundError(clean_name) from err
