import logging

from portfolio_tracker.errors import InsufficientFundsError, InvalidAmountError
from portfolio_tracker.models.account import Account

logger = logging.getLogger(__name__)

account = Account()


def require_positive(label, value):
    if value <= 0:
        raise InvalidAmountError(f"{label} must be greater than zero (got {value})")


def get_cash_balance():
    return account.cash_balance


def deposit(amount):
    require_positive("Deposit amount", amount)
    account.cash_balance += amount
    logger.info("Deposited %.2f; balance is now %.2f", amount, account.cash_balance)
    return account.cash_balance


def debit(amount):
    require_positive("Amount", amount)
    if amount > account.cash_balance:
        raise InsufficientFundsError(
            f"Insufficient funds: need {amount:.2f}, available {account.cash_balance:.2f}"
        )
    account.cash_balance -= amount


def credit(amount):
    if amount < 0:
        raise InvalidAmountError(f"Amount cannot be negative (got {amount})")
    account.cash_balance += amount
