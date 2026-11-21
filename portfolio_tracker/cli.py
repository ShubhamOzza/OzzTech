from decimal import Decimal, InvalidOperation
import logging

from portfolio_tracker.errors import TrackerError
from portfolio_tracker.services import (
    account_service,
    asset_service,
    holding_service,
    portfolio_service,
    price_service,
    transaction_service,
)

logger = logging.getLogger(__name__)

MENU = """
Main Menu
---------
1. Add asset
2. View assets
3. Set asset price
4. Create portfolio
5. View portfolios
6. Select portfolio
7. Delete portfolio
8. View selected portfolio
9. Deposit funds
10. View cash balance
11. Buy asset
12. Sell asset
0. Quit
"""


def ask_number(prompt):
    while True:
        text = input(prompt).strip()
        try:
            number = Decimal(text)
        except InvalidOperation:
            number = None
        # Decimal also accepts "nan" and "inf", which are not usable amounts.
        if number is not None and number.is_finite():
            return number
        print(f"'{text}' is not a number, try again.")


def format_price(value):
    if value is None:
        return "No price set"
    return f"${value:,.2f}"


def add_asset():
    ticker = input("Ticker: ")
    name = input("Asset name: ")
    asset = asset_service.add_asset(ticker, name)
    print(f"Added {asset.ticker} ({asset.name}).")


def view_assets():
    assets = asset_service.list_assets()
    if not assets:
        print("No assets added yet.")
        return
    for asset in assets:
        price = price_service.get_price(asset.ticker)
        print(f"{asset.ticker:8} {asset.name:25} {format_price(price)}")


def set_asset_price():
    ticker = input("Ticker: ")
    price = ask_number("Current price: ")
    price_service.set_price(ticker, price)
    print(f"Updated price for {ticker.strip().upper()} to ${price:,.2f}.")


def create_portfolio():
    name = input("Portfolio name: ")
    strategy = input("Strategy description: ")
    portfolio = portfolio_service.create_portfolio(name, strategy)
    print(f"Created portfolio '{portfolio.name}'.")


def view_portfolios():
    portfolios = portfolio_service.list_portfolios()
    if not portfolios:
        print("No portfolios created yet.")
        return
    selected = portfolio_service.get_selected_portfolio()
    for portfolio in portfolios:
        marker = " (selected)" if portfolio.name == selected else ""
        print(f"- {portfolio.name}: {portfolio.strategy}{marker}")


def select_portfolio():
    name = input("Portfolio name to select: ")
    portfolio = portfolio_service.select_portfolio(name)
    print(f"Selected portfolio '{portfolio.name}'.")


def delete_portfolio():
    name = input("Portfolio name to delete: ")
    portfolio_service.delete_portfolio(name)
    print(f"Deleted portfolio '{name.strip()}'.")


def view_selected_portfolio():
    portfolio_name = portfolio_service.require_selected_portfolio()
    summary = holding_service.get_portfolio_summary(portfolio_name)
    portfolio = summary["portfolio"]
    holdings = summary["holdings"]

    print(f"\nPortfolio: {portfolio.name} ({portfolio.strategy})")
    if not holdings:
        print("No active holdings.")
    else:
        print(
            f"{'Ticker':8} {'Qty':>10} {'Avg Cost':>12} "
            f"{'Price':>12} {'Market Val':>14} {'Unrealized':>14}"
        )
        for h in holdings:
            price_text = format_price(h.current_price)
            mv_text = format_price(h.market_value)
            ug_text = format_price(h.unrealized_gain)
            print(
                f"{h.asset.ticker:8} {h.quantity:>10.4f} ${h.average_cost:>11,.2f} "
                f"{price_text:>12} {mv_text:>14} {ug_text:>14}"
            )

    print(f"\nTotal market value:    ${summary['total_market_value']:,.2f}")
    print(f"Total unrealized gain: ${summary['total_unrealized_gain']:,.2f}")
    print(f"Total realized gain:   ${summary['realized_gain']:,.2f}")


def deposit_funds():
    amount = ask_number("Amount to deposit: ")
    balance = account_service.deposit(amount)
    print(f"Deposited ${amount:,.2f}. Cash balance: ${balance:,.2f}")


def view_cash_balance():
    balance = account_service.get_cash_balance()
    print(f"Cash balance: ${balance:,.2f}")


def buy_asset():
    portfolio_name = portfolio_service.require_selected_portfolio()
    ticker = input("Ticker to buy: ")
    quantity = ask_number("Quantity: ")
    price = ask_number("Price per share: ")
    transaction_service.buy(portfolio_name, ticker, quantity, price)
    print(f"Bought {quantity} shares of {ticker.strip().upper()} in '{portfolio_name}'.")


def sell_asset():
    portfolio_name = portfolio_service.require_selected_portfolio()
    ticker = input("Ticker to sell: ")
    quantity = ask_number("Quantity: ")
    price = ask_number("Price per share: ")
    transaction_service.sell(portfolio_name, ticker, quantity, price)
    print(f"Sold {quantity} shares of {ticker.strip().upper()} from '{portfolio_name}'.")


def run():
    print("Welcome to Portfolio Tracker")
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                add_asset()
            elif choice == "2":
                view_assets()
            elif choice == "3":
                set_asset_price()
            elif choice == "4":
                create_portfolio()
            elif choice == "5":
                view_portfolios()
            elif choice == "6":
                select_portfolio()
            elif choice == "7":
                delete_portfolio()
            elif choice == "8":
                view_selected_portfolio()
            elif choice == "9":
                deposit_funds()
            elif choice == "10":
                view_cash_balance()
            elif choice == "11":
                buy_asset()
            elif choice == "12":
                sell_asset()
            elif choice == "0":
                print("Goodbye.")
                break
            else:
                print(f"'{choice}' is not an option.")
        except TrackerError as error:
            logger.warning("Rejected: %s", error)
            print(f"Sorry: {error}")
