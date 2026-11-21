# Portfolio Tracker

A command-line application for tracking personal investment portfolios, assets, cash deposits, and buy/sell transactions.

## Setup and Running

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Run the application from the project root:

   ```bash
   python -m portfolio_tracker.main
   ```

## Package Layout

- `portfolio_tracker/main.py`: Entry point that configures logging to `tracker.log` and starts the CLI.
- `portfolio_tracker/cli.py`: Command-line menu and input prompts; catches `TrackerError` and prints messages.
- `portfolio_tracker/errors.py`: Defines `TrackerError` and its subclasses for broken business rules.
- `portfolio_tracker/models/account.py`: Defines the `Account` class holding the cash balance.
- `portfolio_tracker/models/asset.py`: Defines the `Asset` class with ticker and name.
- `portfolio_tracker/models/portfolio.py`: Defines the `Portfolio` class with name and strategy.
- `portfolio_tracker/models/transaction.py`: Defines the `Transaction` class recording a buy or sell.
- `portfolio_tracker/models/holding.py`: Defines the `Holding` class that computes market value and unrealized gain.
- `portfolio_tracker/services/account_service.py`: Enforces cash deposit, debit, and credit rules.
- `portfolio_tracker/services/asset_service.py`: Manages adding, finding, and listing assets.
- `portfolio_tracker/services/price_service.py`: Stores and retrieves current prices separately from `Asset`.
- `portfolio_tracker/services/portfolio_service.py`: Manages creating, selecting, listing, and deleting portfolios.
- `portfolio_tracker/services/transaction_service.py`: Enforces buy and sell rules and records transactions.
- `portfolio_tracker/services/holding_service.py`: Calculates holdings, average cost, and portfolio totals from transactions.

## Design Decisions

1. **Are fractional shares allowed?**
   Yes. Any positive share quantity is accepted so users can buy or sell fractional amounts.

2. **Is `aapl` the same asset as `AAPL`?**
   Yes. Tickers are stripped of whitespace and converted to uppercase so `aapl` and `AAPL` refer to the same asset.

3. **Do fully sold positions still appear in the portfolio view?**
   No. Only holdings with a quantity greater than zero are returned in the portfolio holdings list, while realized gains from sold positions remain in the portfolio totals.

4. **How does the portfolio view handle an asset with no current price set?**
   `Holding.market_value` and `Holding.unrealized_gain` return `None` when `current_price` is `None`. The portfolio view shows `"No price set"` for those fields and skips them when adding up total market value and unrealized gain.

5. **Which errors does the user see, and which are only written to the log?**
   Broken business rules (`TrackerError` subclasses) and non-numeric input prompts are shown directly to the user in plain language and logged at `WARNING`. Unexpected exceptions caught in `main()` show a short message to the user while the full traceback is written to `tracker.log` with `logger.exception`.
