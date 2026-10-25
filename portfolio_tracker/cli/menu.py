import logging

from portfolio_tracker.cli.display import (
    format_gain,
    format_money,
    show_assets,
    show_main_menu,
    show_portfolio_summary,
    show_portfolios,
    show_welcome,
)
from portfolio_tracker.cli.prompts import prompt_float, prompt_int, prompt_text
from portfolio_tracker.errors import InvalidInputError, PortfolioTrackerError
from portfolio_tracker.services.asset_service import AssetService
from portfolio_tracker.services.cash_service import CashService
from portfolio_tracker.services.portfolio_service import PortfolioService
from portfolio_tracker.services.pricing_service import PricingService
from portfolio_tracker.services.trading_service import TradingService

logger = logging.getLogger(__name__)


class PortfolioCLI:
    def __init__(
        self,
        asset_service: AssetService,
        pricing_service: PricingService,
        cash_service: CashService,
        portfolio_service: PortfolioService,
        trading_service: TradingService,
    ):
        self._asset_service = asset_service
        self._pricing_service = pricing_service
        self._cash_service = cash_service
        self._portfolio_service = portfolio_service
        self._trading_service = trading_service

    def run(self) -> None:
        show_welcome()

        while True:
            selected = self._portfolio_service.get_selected_portfolio()
            selected_name = selected.name if selected else None
            show_main_menu(self._cash_service.get_balance(), selected_name)

            try:
                choice = prompt_text("Choose an option (0-12): ").strip()
            except (EOFError, KeyboardInterrupt):
                logger.info("CLI exited via interrupt or EOF")
                print("\nGoodbye!")
                return

            if choice == "0":
                logger.info("User chose quit from main menu")
                print("\nGoodbye!")
                return

            self._run_option(choice)

    def _run_option(self, choice: str) -> None:
        try:
            if choice == "1":
                self._add_asset()
            elif choice == "2":
                self._view_assets()
            elif choice == "3":
                self._set_price()
            elif choice == "4":
                self._create_portfolio()
            elif choice == "5":
                self._view_portfolios()
            elif choice == "6":
                self._select_portfolio()
            elif choice == "7":
                self._view_selected_portfolio()
            elif choice == "8":
                self._delete_portfolio()
            elif choice == "9":
                self._deposit_funds()
            elif choice == "10":
                self._view_cash()
            elif choice == "11":
                self._buy_asset()
            elif choice == "12":
                self._sell_asset()
            else:
                raise InvalidInputError(
                    f"'{choice}' is not a valid option. Please enter a number from 0 to 12."
                )
        except PortfolioTrackerError as err:
            # Log refused operations once here where they are caught and shown
            logger.warning("Refused action (%s): %s", type(err).__name__, err)
            print(f"\nError: {err}")
        except (EOFError, KeyboardInterrupt):
            logger.info("User cancelled input during menu action '%s'", choice)
            print("\nCancelled. Returning to main menu.")

    def _add_asset(self) -> None:
        ticker = prompt_text("Enter ticker symbol: ")
        name = prompt_text("Enter asset name: ")
        asset = self._asset_service.add_asset(ticker, name)
        print(f"\nAdded asset {asset.ticker} ({asset.name}).")

    def _view_assets(self) -> None:
        assets = self._pricing_service.get_assets_with_prices()
        show_assets(assets)

    def _set_price(self) -> None:
        ticker = prompt_text("Enter ticker symbol: ")
        price = prompt_float("Enter current price ($): ", "price")
        asset = self._pricing_service.set_price(ticker, price)
        print(f"\nUpdated {asset.ticker} price to {format_money(price)}.")

    def _create_portfolio(self) -> None:
        name = prompt_text("Enter portfolio name: ")
        strategy = prompt_text("Enter investment strategy: ")
        portfolio = self._portfolio_service.create_portfolio(name, strategy)
        print(f"\nCreated portfolio '{portfolio.name}'.")

    def _view_portfolios(self) -> None:
        portfolios = self._portfolio_service.list_portfolios()
        show_portfolios(portfolios)

    def _select_portfolio(self) -> None:
        portfolios = self._portfolio_service.list_portfolios()
        if portfolios:
            show_portfolios(portfolios)
        name = prompt_text("Enter portfolio name to select: ")
        portfolio = self._portfolio_service.select_portfolio(name)
        print(f"\nSelected portfolio '{portfolio.name}'.")

    def _view_selected_portfolio(self) -> None:
        summary = self._portfolio_service.get_selected_portfolio_summary()
        show_portfolio_summary(summary)

    def _delete_portfolio(self) -> None:
        portfolios = self._portfolio_service.list_portfolios()
        if portfolios:
            show_portfolios(portfolios)
        name = prompt_text("Enter portfolio name to delete: ")
        deleted, was_selected = self._portfolio_service.delete_portfolio(name)
        extra = " Selection cleared." if was_selected else ""
        print(f"\nDeleted portfolio '{deleted.name}'.{extra}")

    def _deposit_funds(self) -> None:
        amount = prompt_float("Enter amount to deposit ($): ", "deposit amount")
        balance = self._cash_service.deposit(amount)
        print(
            f"\nDeposited {format_money(amount)}. "
            f"New cash balance: {format_money(balance)}."
        )

    def _view_cash(self) -> None:
        balance = self._cash_service.get_balance()
        print(f"\nCash Balance: {format_money(balance)}")

    def _buy_asset(self) -> None:
        selected = self._portfolio_service.require_selected_portfolio()
        print(f"\nBuying in portfolio: {selected.name}")
        ticker = prompt_text("Enter ticker symbol: ")
        quantity = prompt_int("Enter number of shares to buy: ", "quantity")
        price = prompt_float("Enter buy price per share ($): ", "price")

        trade = self._trading_service.buy_asset(ticker, quantity, price)
        balance = self._cash_service.get_balance()
        print(
            f"\nBought {trade.quantity} shares of {trade.ticker} at "
            f"{format_money(trade.price)}/share (total: {format_money(trade.total)})."
        )
        print(f"Remaining cash balance: {format_money(balance)}")

    def _sell_asset(self) -> None:
        selected = self._portfolio_service.require_selected_portfolio()
        print(f"\nSelling from portfolio: {selected.name}")
        ticker = prompt_text("Enter ticker symbol: ")
        quantity = prompt_int("Enter number of shares to sell: ", "quantity")
        price = prompt_float("Enter sell price per share ($): ", "price")

        trade = self._trading_service.sell_asset(ticker, quantity, price)
        balance = self._cash_service.get_balance()
        gain_text = (
            format_gain(trade.realized_gain)
            if trade.realized_gain is not None
            else "$0.00"
        )
        print(
            f"\nSold {trade.quantity} shares of {trade.ticker} at "
            f"{format_money(trade.price)}/share (proceeds: {format_money(trade.total)}, "
            f"realized gain/loss: {gain_text})."
        )
        print(f"New cash balance: {format_money(balance)}")
