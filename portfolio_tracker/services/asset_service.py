import logging

from portfolio_tracker.domain.asset import Asset
from portfolio_tracker.errors import (
    AssetNotFoundError,
    DuplicateAssetError,
    InvalidNameError,
    InvalidTickerError,
)

logger = logging.getLogger(__name__)


def normalize_ticker(ticker: str) -> str:
    cleaned = ticker.strip().upper()
    if not cleaned:
        raise InvalidTickerError("Ticker cannot be empty.")
    if " " in cleaned or "\t" in cleaned:
        raise InvalidTickerError("Ticker cannot contain spaces.")
    return cleaned


class AssetService:
    def __init__(self):
        self._assets: dict[str, Asset] = {}

    def add_asset(self, ticker: str, name: str) -> Asset:
        clean_ticker = normalize_ticker(ticker)
        clean_name = name.strip()
        if not clean_name:
            raise InvalidNameError("Asset name cannot be empty.")

        if clean_ticker in self._assets:
            raise DuplicateAssetError(clean_ticker)

        asset = Asset(clean_ticker, clean_name)
        self._assets[clean_ticker] = asset
        logger.info("Added asset %s (%s)", asset.ticker, asset.name)
        return asset

    def get_asset(self, ticker: str) -> Asset:
        clean_ticker = normalize_ticker(ticker)
        try:
            return self._assets[clean_ticker]
        except KeyError as err:
            raise AssetNotFoundError(clean_ticker) from err

    def list_assets(self) -> list[Asset]:
        return sorted(self._assets.values(), key=lambda a: a.ticker)
