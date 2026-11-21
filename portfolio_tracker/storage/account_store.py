from decimal import Decimal

from portfolio_tracker.models.account import Account

ACCOUNT_ID = 1


def get_account(session):
    account = session.get(Account, ACCOUNT_ID)
    if account is None:
        account = Account(id=ACCOUNT_ID, cash_balance=Decimal("0"))
        session.add(account)
    return account


def get_cash_balance(session):
    return get_account(session).cash_balance


def set_cash_balance(session, amount):
    get_account(session).cash_balance = amount
