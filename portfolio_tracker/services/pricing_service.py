import logging
import math

from portfolio_tracker.domain.asset import Asset
from portfolio_tracker.errors import InvalidPriceError
from portfolio_tracker.services.asset_service import AssetService

logger = logging.getLogger(__name__)


class PricingService:
    def __init__(self, asset_service: AssetService):
        self._asset_service = asset_service
        self._prices: dict[str, float] = {}

    def set_price(self, ticker: str, price: float) -> Asset:
        asset = self._asset_service.get_asset(ticker)
        if math.isnan(price) or math.isinf(price) or price < 0:
            raise InvalidPriceError("Price must be zero or more.")

        self._prices[asset.ticker] = price
        logger.info("Set current price for %s to %.2f", asset.ticker, price)
        return asset

    def get_price(self, ticker: str) -> float | None:
        asset = self._asset_service.get_asset(ticker)
        return self._prices.get(asset.ticker)

    def get_assets_with_prices(self) -> list[dict]:
        items = []
        for asset in self._asset_service.list_assets():
            items.append(
                {
                    "ticker": asset.ticker,
                    "name": asset.name,
                    "price": self._prices.get(asset.ticker),
                }
            )
        return items
