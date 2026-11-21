# Portfolio Tracker

A command-line application for tracking personal investment portfolios, assets, cash deposits, and buy/sell transactions. Data is stored in a MySQL database using SQLAlchemy, and business rules and calculations are tested with pytest against an in-memory SQLite database.

## 1. Setup and Running the App

### Virtual Environment and Dependencies

From the project root folder:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

(On macOS/Linux, activate with `source .venv/bin/activate`.)

### MySQL Database and User Setup

1. Make sure your local MySQL server is running, then log in as `root`:

   ```bash
   mysql -u root -p
   ```

2. Create the `portfolio_tracker` database and the `tracker` user (replace `choose-a-password` with your own password):

   ```sql
   CREATE DATABASE portfolio_tracker;
   CREATE USER 'tracker'@'localhost' IDENTIFIED BY 'choose-a-password';
   GRANT ALL PRIVILEGES ON portfolio_tracker.* TO 'tracker'@'localhost';
   EXIT;
   ```

### Settings File (`.env`)

Copy `.env.example` to `.env` in the project root and fill in your MySQL settings:

```text
DB_HOST=localhost
DB_PORT=3306
DB_USER=tracker
DB_PASSWORD=choose-a-password
DB_NAME=portfolio_tracker
```

### Run the App

From the project root:

```bash
python -m portfolio_tracker.main
```

The app automatically creates any missing tables on startup and writes logs to `tracker.log`.

## 2. Running the Tests

From the project root with the virtual environment active:

```bash
python -m pytest
```

For verbose output showing each test name:

```bash
python -m pytest -v
```

## 3. Package Layout

- `portfolio_tracker/main.py`: Entry point that configures logging to `tracker.log`, creates missing database tables, and starts the CLI.
- `portfolio_tracker/cli.py`: Command-line menu and input prompts; converts numeric input to `Decimal` and catches `TrackerError`.
- `portfolio_tracker/database.py`: Creates the SQLAlchemy engine from `.env`, defines `Base`, `create_tables()`, and the `transaction()` session helper.
- `portfolio_tracker/errors.py`: Defines `TrackerError` and its subclasses for broken business rules.
- `portfolio_tracker/models/account.py`: SQLAlchemy model for the `account` table holding the shared `cash_balance`.
- `portfolio_tracker/models/asset.py`: SQLAlchemy model for the `assets` table with `id`, unique `ticker`, and `name`.
- `portfolio_tracker/models/portfolio.py`: SQLAlchemy model for the `portfolios` table with `id`, unique `name`, and `strategy`.
- `portfolio_tracker/models/transaction.py`: SQLAlchemy model for the `transactions` table with foreign keys and relationships to `Portfolio` and `Asset`.
- `portfolio_tracker/models/holding.py`: Plain Python class representing a calculated position and its `market_value` and `unrealized_gain`.
- `portfolio_tracker/storage/account_store.py`: Reads and updates the single account row in the database.
- `portfolio_tracker/storage/asset_store.py`: Saves and queries `Asset` rows in the database.
- `portfolio_tracker/storage/portfolio_store.py`: Saves, queries, and deletes `Portfolio` rows in the database.
- `portfolio_tracker/storage/transaction_store.py`: Saves, lists, and deletes `Transaction` rows for a portfolio.
- `portfolio_tracker/storage/price_store.py`: Keeps the in-memory dictionary of current asset prices.
- `portfolio_tracker/services/account_service.py`: Enforces cash deposit, debit, and credit rules inside database transactions.
- `portfolio_tracker/services/asset_service.py`: Enforces ticker normalization, uniqueness, and lookup rules.
- `portfolio_tracker/services/price_service.py`: Validates and stores current market prices separately from `Asset`.
- `portfolio_tracker/services/portfolio_service.py`: Enforces portfolio creation, selection, lookup, and empty-only deletion rules.
- `portfolio_tracker/services/transaction_service.py`: Enforces buy and sell rules and records trades and cash updates in one transaction.
- `portfolio_tracker/services/holding_service.py`: Calculates active holdings, weighted-average cost, and realized/unrealized gains from stored transactions.

## 4. Design Decisions

### Assignment 2 Decisions

1. **Are current prices stored in the database, or kept in memory and re-entered each run?**
   Current prices are kept in memory in `price_store.py` (`current_prices = {}`) and re-entered each run. Since a later milestone replaces manual prices with a live market-data feed, keeping prices in a separate in-memory store avoids adding a database table that would soon be thrown away while keeping the price lookup behind `price_service.get_price()` so it is easy to mock in tests and replace later.

2. **How many decimal places do you store for cash, share quantities, and prices, and what does that mean for rounding?**
   `cash_balance` uses `Numeric(14, 2)` (2 decimal places for cents), while `quantity` and `price_per_share` use `Numeric(14, 4)` (4 decimal places for fractional shares and sub-penny share prices). All numbers are converted to `Decimal` at input time so floats are never used. When a trade changes the cash balance, the dollar amount is rounded to 2 decimal places (`round(amount, 2)`). For example, if the account has `$100.00` and someone buys `3` shares at `$33.3333`, the raw cost is `3 * 33.3333 = $99.9999`, which rounds to `$100.00` in cents, reducing the stored cash balance to `$0.00`.

3. **Which of your business rules does the database itself enforce, in addition to the checks in your Python code, and why those?**
   In addition to the checks in the service modules, the database enforces:
   - `UNIQUE` constraints on `portfolios.name` and `assets.ticker` so duplicate portfolio names or asset tickers can never be stored even if a bug in Python skipped the check.
   - `NOT NULL` constraints on every column (`cash_balance`, `name`, `strategy`, `ticker`, `portfolio_id`, `asset_id`, `side`, `quantity`, `price_per_share`, `trade_date`) so incomplete records cannot be inserted.
   - `FOREIGN KEY` constraints on `transactions.portfolio_id` and `transactions.asset_id` so every trade must reference a real portfolio and a real asset.
   - `Enum("buy", "sell")` on `transactions.side` so only valid trade directions can be recorded.
   The database acts as the final line of defense to protect stored data integrity if application code ever has a bug.

### Assignment 1 Decisions

1. **Are fractional shares allowed?**
   Yes, positive `Decimal` quantities up to 4 decimal places are supported.
2. **Is `aapl` the same asset as `AAPL`?**
   Yes, tickers are stripped and converted to uppercase.
3. **Do fully sold positions still appear in the portfolio view?**
   No, positions whose quantity reaches `0` are left out of the active holdings list while their realized gains stay in the portfolio totals.
4. **How does the portfolio view handle an asset with no current price set?**
   `Holding.market_value` and `Holding.unrealized_gain` return `None`, which the CLI displays as `"No price set"` and skips when summing portfolio market value and unrealized gain.
5. **Which errors does the user see, and which are only written to the log?**
   `TrackerError` refusals and invalid number inputs are shown to the user in plain language and logged at `WARNING`; unexpected exceptions show a generic message on screen and log the full traceback to `tracker.log` with `logger.exception`.

## 5. How the Tests Work

### Fresh In-Memory Database per Test

In `portfolio_tracker/database.py`, the database engine is created inside `get_engine()` rather than at import time, and `transaction()` calls `get_engine()` whenever a service opens a transaction. In `tests/conftest.py`, the `empty_db` fixture creates a brand-new in-memory SQLite engine (`create_engine("sqlite://", poolclass=StaticPool)`), creates all tables on it with `database.Base.metadata.create_all(engine)`, and uses `monkeypatch.setattr(database, "get_engine", lambda: engine)` to swap in that in-memory engine for the duration of the test. It also resets the in-memory `price_store.current_prices` and `portfolio_store.selection` dictionaries before yielding, and disposes the engine after the test finishes.

This matters for three reasons:
1. Running the test suite never adds fake deposits, portfolios, or trades to the real MySQL database.
2. Every test starts from the exact same known empty state (zero cash, no portfolios, no assets, no prices), so results do not depend on what was already in MySQL.
3. No test can leak data into a later test, so tests are repeatable and pass in any order.

### Deliberate Bug and Failure Report

To verify the boundary test for positive deposits, I temporarily changed `require_positive` in `portfolio_tracker/services/account_service.py` from `if value <= Decimal("0"):` to `if value < Decimal("0"):` so that a deposit of `0` was not rejected.

Running `python -m pytest` caught the bug immediately in `tests/test_account_service.py::test_deposit_must_be_positive[amount0]` (while `amount1` with `-50` still passed, showing why testing the boundary `0` matters):

```text
___________________ test_deposit_must_be_positive[amount0] ____________________

empty_db = None, amount = Decimal('0')

    @pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-50")])
    def test_deposit_must_be_positive(empty_db, amount):
>       with pytest.raises(InvalidAmountError):
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE InvalidAmountError

tests\test_account_service.py:22: Failed
=========================== short test summary info ===========================
FAILED tests/test_account_service.py::test_deposit_must_be_positive[amount0]
======================== 1 failed, 56 passed in 2.64s =========================
```

Changing `<` back to `<=` made all 57 tests pass again.
