from decimal import Decimal

import pytest

from portfolio_tracker.errors import (
    InsufficientFundsError,
    InsufficientSharesError,
    InvalidAmountError,
    NoPortfolioSelectedError,
    NotFoundError,
)
from portfolio_tracker.services import (
    account_service,
    asset_service,
    holding_service,
    portfolio_service,
    transaction_service,
)


def test_buy_takes_the_cost_out_of_cash(funded_portfolio):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("3"), Decimal("100"))

    assert account_service.get_cash_balance() == Decimal("700")


def test_buy_rounds_cash_cost_to_cents(empty_db):
    account_service.deposit(Decimal("100"))
    portfolio_service.create_portfolio("Tech growth", "Large-cap tech")
    asset_service.add_asset("AAPL", "Apple Inc.")

    transaction_service.buy("Tech growth", "AAPL", Decimal("3"), Decimal("33.3333"))

    assert account_service.get_cash_balance() == Decimal("0.00")


def test_buying_with_no_portfolio_selected_changes_nothing(funded_portfolio):
    with pytest.raises(NoPortfolioSelectedError):
        transaction_service.buy(None, "AAPL", Decimal("3"), Decimal("100"))

    assert account_service.get_cash_balance() == Decimal("1000")
    assert holding_service.get_holdings(funded_portfolio) == []


def test_buying_into_unknown_portfolio_changes_nothing(funded_portfolio):
    with pytest.raises(NotFoundError):
        transaction_service.buy("Unknown", "AAPL", Decimal("3"), Decimal("100"))

    assert account_service.get_cash_balance() == Decimal("1000")


def test_buying_an_unknown_ticker_changes_nothing(funded_portfolio):
    with pytest.raises(NotFoundError):
        transaction_service.buy(funded_portfolio, "ZZZZ", Decimal("3"), Decimal("100"))

    assert account_service.get_cash_balance() == Decimal("1000")
    assert holding_service.get_holdings(funded_portfolio) == []


@pytest.mark.parametrize("quantity", [Decimal("0"), Decimal("-2")])
def test_buy_quantity_must_be_positive(funded_portfolio, quantity):
    with pytest.raises(InvalidAmountError):
        transaction_service.buy(funded_portfolio, "AAPL", quantity, Decimal("100"))

    assert account_service.get_cash_balance() == Decimal("1000")
    assert holding_service.get_holdings(funded_portfolio) == []


@pytest.mark.parametrize("price", [Decimal("0"), Decimal("-10")])
def test_buy_price_must_be_positive(funded_portfolio, price):
    with pytest.raises(InvalidAmountError):
        transaction_service.buy(funded_portfolio, "AAPL", Decimal("3"), price)

    assert account_service.get_cash_balance() == Decimal("1000")
    assert holding_service.get_holdings(funded_portfolio) == []


def test_buying_more_than_cash_balance_changes_nothing(funded_portfolio):
    with pytest.raises(InsufficientFundsError):
        transaction_service.buy(funded_portfolio, "AAPL", Decimal("20"), Decimal("100"))

    assert account_service.get_cash_balance() == Decimal("1000")
    assert holding_service.get_holdings(funded_portfolio) == []


def test_sell_adds_proceeds_to_cash(funded_portfolio):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("5"), Decimal("100"))

    transaction_service.sell(funded_portfolio, "AAPL", Decimal("2"), Decimal("120"))

    assert account_service.get_cash_balance() == Decimal("740")


def test_selling_worthless_position_at_zero_price_is_allowed(funded_portfolio):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))

    transaction_service.sell(funded_portfolio, "AAPL", Decimal("4"), Decimal("0"))

    assert account_service.get_cash_balance() == Decimal("600")
    assert holding_service.get_holdings(funded_portfolio) == []


def test_selling_with_no_portfolio_selected_changes_nothing(funded_portfolio):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))

    with pytest.raises(NoPortfolioSelectedError):
        transaction_service.sell(None, "AAPL", Decimal("2"), Decimal("100"))

    assert account_service.get_cash_balance() == Decimal("600")
    [holding] = holding_service.get_holdings(funded_portfolio)
    assert holding.quantity == Decimal("4")


def test_selling_unknown_ticker_changes_nothing(funded_portfolio):
    with pytest.raises(NotFoundError):
        transaction_service.sell(funded_portfolio, "ZZZZ", Decimal("1"), Decimal("100"))

    assert account_service.get_cash_balance() == Decimal("1000")


@pytest.mark.parametrize("quantity", [Decimal("0"), Decimal("-1")])
def test_sell_quantity_must_be_positive(funded_portfolio, quantity):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))

    with pytest.raises(InvalidAmountError):
        transaction_service.sell(funded_portfolio, "AAPL", quantity, Decimal("110"))

    assert account_service.get_cash_balance() == Decimal("600")
    [holding] = holding_service.get_holdings(funded_portfolio)
    assert holding.quantity == Decimal("4")


def test_sell_price_cannot_be_negative(funded_portfolio):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))

    with pytest.raises(InvalidAmountError):
        transaction_service.sell(funded_portfolio, "AAPL", Decimal("2"), Decimal("-5"))

    assert account_service.get_cash_balance() == Decimal("600")
    [holding] = holding_service.get_holdings(funded_portfolio)
    assert holding.quantity == Decimal("4")


def test_selling_more_shares_than_held_is_refused(funded_portfolio):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))

    with pytest.raises(InsufficientSharesError):
        transaction_service.sell(funded_portfolio, "AAPL", Decimal("5"), Decimal("110"))

    assert account_service.get_cash_balance() == Decimal("600")
    [holding] = holding_service.get_holdings(funded_portfolio)
    assert holding.quantity == Decimal("4")


def test_selling_shares_held_only_in_another_portfolio_is_refused(funded_portfolio):
    portfolio_service.create_portfolio("Dividend income", "Dividend stocks")
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))

    with pytest.raises(InsufficientSharesError):
        transaction_service.sell("Dividend income", "AAPL", Decimal("1"), Decimal("110"))

    assert account_service.get_cash_balance() == Decimal("600")
    [holding] = holding_service.get_holdings(funded_portfolio)
    assert holding.quantity == Decimal("4")
