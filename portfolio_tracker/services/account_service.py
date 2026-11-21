from decimal import Decimal
import logging

from portfolio_tracker import database
from portfolio_tracker.errors import InsufficientFundsError, InvalidAmountError
from portfolio_tracker.storage import account_store

logger = logging.getLogger(__name__)


def require_positive(label, value):
    if value <= Decimal("0"):
        raise InvalidAmountError(f"{label} must be greater than zero (got {value})")


def get_cash_balance():
    with database.transaction() as session:
        return account_store.get_cash_balance(session)


def deposit(amount):
    require_positive("Deposit amount", amount)
    rounded = round(amount, 2)
    with database.transaction() as session:
        new_balance = round(account_store.get_cash_balance(session) + rounded, 2)
        account_store.set_cash_balance(session, new_balance)
    logger.info("Deposited %.2f; balance is now %.2f", rounded, new_balance)
    return new_balance


def debit(session, amount):
    require_positive("Amount", amount)
    rounded = round(amount, 2)
    balance = account_store.get_cash_balance(session)
    if rounded > balance:
        raise InsufficientFundsError(
            f"Insufficient funds: need {rounded:.2f}, available {balance:.2f}"
        )
    new_balance = round(balance - rounded, 2)
    account_store.set_cash_balance(session, new_balance)
    return new_balance


def credit(session, amount):
    if amount < Decimal("0"):
        raise InvalidAmountError(f"Amount cannot be negative (got {amount})")
    rounded = round(amount, 2)
    balance = account_store.get_cash_balance(session)
    new_balance = round(balance + rounded, 2)
    account_store.set_cash_balance(session, new_balance)
    return new_balance
