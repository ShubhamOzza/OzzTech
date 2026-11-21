from decimal import Decimal

import pytest

from portfolio_tracker.errors import InvalidAmountError
from portfolio_tracker.services import account_service


def test_new_account_starts_with_no_cash(empty_db):
    assert account_service.get_cash_balance() == Decimal("0")


def test_deposits_add_up(empty_db):
    account_service.deposit(Decimal("500"))
    account_service.deposit(Decimal("150.25"))

    assert account_service.get_cash_balance() == Decimal("650.25")


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("-50")])
def test_deposit_must_be_positive(empty_db, amount):
    with pytest.raises(InvalidAmountError):
        account_service.deposit(amount)

    assert account_service.get_cash_balance() == Decimal("0")


def test_deposit_rounds_to_two_decimal_places(empty_db):
    account_service.deposit(Decimal("10.556"))

    assert account_service.get_cash_balance() == Decimal("10.56")
