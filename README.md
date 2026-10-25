# OzzTech - Portfolio Tracker

A command-line investment portfolio tracker built in Python. You can add assets, set their current market prices, deposit cash into a shared balance, create named portfolios for different strategies, buy and sell shares, and view unrealized and realized gains and losses.

The code separates domain objects, business-rule services, custom errors, and the CLI so the terminal interface can later be swapped out for a web API and frontend without rewriting the core rules.

## Setup and Running the App

1. Open a terminal in the project root folder and create a virtual environment:

   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:

   - **Windows (PowerShell):**
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt):**
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **macOS / Linux:**
     ```bash
     source .venv/bin/activate
     ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the app as a Python package:

   ```bash
   python -m portfolio_tracker.main
   ```

Logs are written to `portfolio_tracker.log` in the project root so they do not clutter the terminal screen.

## Package Layout

```text
portfolio_tracker/
  __init__.py
  main.py
  errors.py
  domain/
    __init__.py
    asset.py
    account.py
    portfolio.py
  services/
    __init__.py
    asset_service.py
    pricing_service.py
    cash_service.py
    portfolio_service.py
    trading_service.py
  cli/
    __init__.py
    prompts.py
    display.py
    menu.py
```

- `portfolio_tracker/__init__.py` - Marks `portfolio_tracker` as a Python package.
- `portfolio_tracker/main.py` - Entry point that configures file logging once, wires up the services, and starts the CLI.
- `portfolio_tracker/errors.py` - Defines the base `PortfolioTrackerError` class and specific subclasses for input, validation, lookup, duplicate, and trading errors.
- `portfolio_tracker/domain/__init__.py` - Package marker for domain classes.
- `portfolio_tracker/domain/asset.py` - Defines the `Asset` class holding ticker and asset name.
- `portfolio_tracker/domain/account.py` - Defines the `CashAccount` class holding the shared cash balance.
- `portfolio_tracker/domain/portfolio.py` - Defines `Portfolio`, `Position`, and `Trade` classes for holdings, trade records, and realized gains.
- `portfolio_tracker/services/__init__.py` - Package marker for service modules.
- `portfolio_tracker/services/asset_service.py` - Handles adding, normalizing, listing, and looking up assets.
- `portfolio_tracker/services/pricing_service.py` - Stores and retrieves current asset prices separately from `Asset` so a live price feed can replace it later.
- `portfolio_tracker/services/cash_service.py` - Manages cash deposits and updates the shared cash balance during buys and sells.
- `portfolio_tracker/services/portfolio_service.py` - Handles creating, listing, selecting, deleting, and calculating summary values for portfolios.
- `portfolio_tracker/services/trading_service.py` - Enforces buy and sell rules, calculates weighted-average cost, and records realized gains.
- `portfolio_tracker/cli/__init__.py` - Package marker for command-line interface modules.
- `portfolio_tracker/cli/prompts.py` - Reads user text and parses integers and floats from standard input.
- `portfolio_tracker/cli/display.py` - Formats dollar amounts and prints menus, asset lists, and portfolio tables.
- `portfolio_tracker/cli/menu.py` - Runs the welcome screen and main menu loop, calls service methods, and catches errors to show plain-language messages.

## Design Decisions

1. **Are fractional shares allowed?**
   - **Choice:** No, only whole shares (positive integers) are allowed.
   - **Why:** Whole-share quantities keep share counts simple to read and avoid floating-point rounding leftovers when selling off an entire position (so checking whether a portfolio holds `0` shares before deletion is always exact).

2. **Is `aapl` the same asset as `AAPL`?**
   - **Choice:** Yes. Tickers are trimmed and converted to uppercase whenever they are added or looked up.
   - **Why:** Real stock tickers are not case-sensitive, and treating `aapl` and `AAPL` as two different assets would make it easy to accidentally add duplicates or look up the wrong symbol when trading. Portfolio names are also matched case-insensitively for the same reason while keeping their original display capitalization.

3. **Do fully sold positions still appear in the portfolio view?**
   - **Choice:** No. Once a position's quantity reaches `0`, it is removed from the active holdings table, while its realized gain/loss stays in the portfolio totals.
   - **Why:** The holdings table is meant to show what the portfolio currently owns. Leaving old `0`-share rows in the table adds clutter over time, while keeping `realized_gain` on the `Portfolio` object preserves the profit/loss history from closed trades.

4. **How does the portfolio view handle an asset with no current price set?**
   - **Choice:** The row shows `N/A` for current price, market value, and unrealized gain/loss, excludes that asset from the market value and unrealized gain/loss totals, and prints a note listing any held tickers that still need a price.
   - **Why:** Since trade prices and market prices are separate, a user can buy an asset before setting its current market price. Treating a missing price as `$0` would show a fake 100% unrealized loss, and using average cost would pretend the price has not moved. Showing `N/A` with a clear note prevents crashes without making up numbers.

5. **Which errors does the user see, and which are only written to the log?**
   - **Choice:** Invalid inputs (bad menu choices, typing letters instead of numbers) and broken business rules (duplicates, unknown tickers/portfolios, no selected portfolio, not enough cash or shares, deleting a portfolio that still holds shares) are shown directly to the user in plain English and logged as `WARNING` where handled. Unexpected internal exceptions only show a short friendly message on screen while the full Python traceback is written to `portfolio_tracker.log` as `ERROR` (alongside normal `INFO` logs for successful actions).
   - **Why:** Users need clear explanations for input mistakes and rule refusals so they know how to fix them, whereas raw stack traces and internal Python errors (`KeyError`, `ValueError`, etc.) are not helpful to an end user and belong in the log file for debugging.
