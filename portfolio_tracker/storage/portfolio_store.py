from sqlalchemy import select

from portfolio_tracker.models.portfolio import Portfolio

selection = {"name": None}


def add_portfolio(session, portfolio):
    session.add(portfolio)


def get_portfolio(session, name):
    return session.scalars(select(Portfolio).filter_by(name=name)).first()


def get_all_portfolios(session):
    return session.scalars(select(Portfolio)).all()


def delete_portfolio(session, portfolio):
    session.delete(portfolio)


def get_selected_name():
    return selection["name"]


def set_selected_name(name):
    selection["name"] = name

