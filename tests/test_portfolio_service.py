from decimal import Decimal

import pytest

from portfolio_tracker.errors import (
    DuplicateError,
    InvalidInputError,
    NoPortfolioSelectedError,
    NotFoundError,
    PortfolioNotEmptyError,
)
from portfolio_tracker.services import (
    account_service,
    holding_service,
    portfolio_service,
    transaction_service,
)


def test_created_portfolio_appears_in_list(empty_db):
    portfolio_service.create_portfolio("Tech growth", "Large-cap tech")

    [portfolio] = portfolio_service.list_portfolios()

    assert portfolio.name == "Tech growth"
    assert portfolio.strategy == "Large-cap tech"


def test_portfolio_names_are_unique(empty_db):
    portfolio_service.create_portfolio("Tech growth", "Large-cap tech")

    with pytest.raises(DuplicateError):
        portfolio_service.create_portfolio("Tech growth", "A different strategy")

    [portfolio] = portfolio_service.list_portfolios()
    assert portfolio.strategy == "Large-cap tech"


def test_empty_portfolio_name_is_refused(empty_db):
    with pytest.raises(InvalidInputError):
        portfolio_service.create_portfolio("   ", "Large-cap tech")

    assert portfolio_service.list_portfolios() == []


def test_empty_portfolio_strategy_is_refused(empty_db):
    with pytest.raises(InvalidInputError):
        portfolio_service.create_portfolio("Tech growth", "   ")

    assert portfolio_service.list_portfolios() == []


def test_selecting_portfolio_records_active_selection(empty_db):
    portfolio_service.create_portfolio("Tech growth", "Large-cap tech")

    portfolio_service.select_portfolio("Tech growth")

    assert portfolio_service.get_selected_portfolio() == "Tech growth"


def test_selecting_unknown_portfolio_is_refused(empty_db):
    with pytest.raises(NotFoundError):
        portfolio_service.select_portfolio("Missing")

    assert portfolio_service.get_selected_portfolio() is None


def test_requiring_selected_portfolio_when_none_is_selected_raises_error(empty_db):
    with pytest.raises(NoPortfolioSelectedError):
        portfolio_service.require_selected_portfolio()


def test_deleting_portfolio_with_open_holdings_is_refused(funded_portfolio):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("2"), Decimal("100"))

    with pytest.raises(PortfolioNotEmptyError):
        portfolio_service.delete_portfolio(funded_portfolio)

    assert len(portfolio_service.list_portfolios()) == 1
    assert len(holding_service.get_holdings(funded_portfolio)) == 1


def test_deleting_portfolio_after_selling_all_shares_removes_it_and_clears_selection(
    funded_portfolio,
):
    portfolio_service.select_portfolio(funded_portfolio)
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("2"), Decimal("100"))
    transaction_service.sell(funded_portfolio, "AAPL", Decimal("2"), Decimal("120"))

    portfolio_service.delete_portfolio(funded_portfolio)

    assert portfolio_service.list_portfolios() == []
    assert portfolio_service.get_selected_portfolio() is None
    assert account_service.get_cash_balance() == Decimal("1040")


def test_deleting_unknown_portfolio_is_refused(empty_db):
    with pytest.raises(NotFoundError):
        portfolio_service.delete_portfolio("Missing")
