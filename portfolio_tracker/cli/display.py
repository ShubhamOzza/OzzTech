def format_money(amount: float) -> str:
    rounded = round(amount, 2)
    if rounded == 0:
        rounded = 0.0
    if rounded < 0:
        return f"-${abs(rounded):,.2f}"
    return f"${rounded:,.2f}"


def format_gain(amount: float) -> str:
    rounded = round(amount, 2)
    if rounded == 0:
        return "$0.00"
    if rounded > 0:
        return f"+${rounded:,.2f}"
    return f"-${abs(rounded):,.2f}"


def show_welcome() -> None:
    print("\n============================================================")
    print("               PERSONAL PORTFOLIO TRACKER")
    print("============================================================")
    print("Manage assets, build investment portfolios, deposit cash,")
    print("buy and sell shares, and track your gains and losses.")


def show_main_menu(cash_balance: float, selected_name: str | None) -> None:
    active_text = selected_name if selected_name else "None"
    print("\n------------------------------------------------------------")
    print(f"Cash Balance: {format_money(cash_balance)} | Selected Portfolio: {active_text}")
    print("------------------------------------------------------------")
    print("Assets:")
    print("  1. Add an asset")
    print("  2. View assets")
    print("  3. Set an asset's current price")
    print("\nPortfolios:")
    print("  4. Create a portfolio")
    print("  5. View portfolios")
    print("  6. Select a portfolio")
    print("  7. View selected portfolio")
    print("  8. Delete a portfolio")
    print("\nCash & Trading:")
    print("  9. Deposit funds")
    print(" 10. View cash balance")
    print(" 11. Buy an asset")
    print(" 12. Sell an asset")
    print("\n  0. Quit")
    print("------------------------------------------------------------")


def show_assets(assets: list[dict]) -> None:
    if not assets:
        print("\nNo assets have been added yet.")
        return

    print("\nAssets:")
    print(f"{'Ticker':<10} {'Name':<26} {'Current Price':>15}")
    print("-" * 53)
    for item in assets:
        price_str = (
            format_money(item["price"])
            if item["price"] is not None
            else "No price set"
        )
        print(f"{item['ticker']:<10} {item['name']:<26} {price_str:>15}")


def show_portfolios(portfolios: list[dict]) -> None:
    if not portfolios:
        print("\nNo portfolios have been created yet.")
        return

    print("\nPortfolios:")
    print(f"{'Selected':<10} {'Name':<22} {'Strategy'}")
    print("-" * 60)
    selected_name = "None"
    for item in portfolios:
        marker = "* Yes" if item["is_selected"] else ""
        if item["is_selected"]:
            selected_name = item["name"]
        print(f"{marker:<10} {item['name']:<22} {item['strategy']}")
    print(f"\nCurrently selected: {selected_name}")


def show_portfolio_summary(summary: dict) -> None:
    print(f"\nPortfolio: {summary['name']}")
    print(f"Strategy:  {summary['strategy']}\n")

    positions = summary["positions"]
    if not positions:
        print("No shares are currently held in this portfolio.")
    else:
        print(
            f"{'Ticker':<8} {'Name':<20} {'Qty':>7} {'Avg Cost':>12} "
            f"{'Curr Price':>12} {'Market Val':>14} {'Unrealized G/L':>15}"
        )
        print("-" * 94)
        for pos in positions:
            curr_price = (
                format_money(pos["current_price"])
                if pos["current_price"] is not None
                else "N/A"
            )
            market_val = (
                format_money(pos["market_value"])
                if pos["market_value"] is not None
                else "N/A"
            )
            unrealized = (
                format_gain(pos["unrealized_gain"])
                if pos["unrealized_gain"] is not None
                else "N/A"
            )
            print(
                f"{pos['ticker']:<8} {pos['name']:<20} {pos['quantity']:>7} "
                f"{format_money(pos['average_cost']):>12} {curr_price:>12} "
                f"{market_val:>14} {unrealized:>15}"
            )

    print("\nPortfolio Totals:")
    print(f"  Market Value:         {format_money(summary['total_market_value'])}")
    print(f"  Unrealized Gain/Loss: {format_gain(summary['total_unrealized_gain'])}")
    print(f"  Realized Gain/Loss:   {format_gain(summary['total_realized_gain'])}")

    if summary["unpriced_tickers"]:
        missing = ", ".join(summary["unpriced_tickers"])
        print(
            f"\nNote: No current price set for {missing}. "
            "Unpriced holdings show 'N/A' and are excluded from Market Value "
            "and Unrealized Gain/Loss totals."
        )
