from sqlalchemy import select

from portfolio_tracker.models.asset import Asset


def add_asset(session, asset):
    session.add(asset)


def get_asset(session, ticker):
    return session.scalars(select(Asset).filter_by(ticker=ticker)).first()


def get_all_assets(session):
    return session.scalars(select(Asset)).all()
