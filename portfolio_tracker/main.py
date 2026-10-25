import logging

from portfolio_tracker.cli.menu import PortfolioCLI
from portfolio_tracker.services.asset_service import AssetService
from portfolio_tracker.services.cash_service import CashService
from portfolio_tracker.services.portfolio_service import PortfolioService
from portfolio_tracker.services.pricing_service import PricingService
from portfolio_tracker.services.trading_service import TradingService

LOG_FILE = "portfolio_tracker.log"

logger = logging.getLogger("portfolio_tracker.main")


def setup_logging() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


def create_cli() -> PortfolioCLI:
    asset_service = AssetService()
    pricing_service = PricingService(asset_service)
    cash_service = CashService()
    portfolio_service = PortfolioService(asset_service, pricing_service)
    trading_service = TradingService(asset_service, cash_service, portfolio_service)
    return PortfolioCLI(
        asset_service,
        pricing_service,
        cash_service,
        portfolio_service,
        trading_service,
    )


def main() -> None:
    setup_logging()
    logger.info("Application started")
    try:
        app = create_cli()
        app.run()
    except Exception:
        logger.exception("Unexpected error stopped the application")
        print(
            "\nSomething went wrong unexpectedly. "
            "Details were recorded in portfolio_tracker.log."
        )
    else:
        logger.info("Application finished cleanly")


if __name__ == "__main__":
    main()
