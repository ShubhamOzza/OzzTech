from sqlalchemy import select

from portfolio_tracker.models.transaction import Transaction


def add_transaction(session, transaction):
    session.add(transaction)


def get_transactions(session, portfolio):
    return session.scalars(select(Transaction).filter_by(portfolio=portfolio)).all()


def delete_transactions(session, portfolio):
    for transaction in get_transactions(session, portfolio):
        session.delete(transaction)
