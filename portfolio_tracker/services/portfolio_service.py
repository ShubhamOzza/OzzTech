import logging

from portfolio_tracker import database
from portfolio_tracker.errors import (
    DuplicateError,
    InvalidInputError,
    NoPortfolioSelectedError,
    NotFoundError,
    PortfolioNotEmptyError,
)
from portfolio_tracker.models.portfolio import Portfolio
from portfolio_tracker.services import holding_service
from portfolio_tracker.storage import portfolio_store, transaction_store

logger = logging.getLogger(__name__)

selected_portfolio = None


def create_portfolio(name, strategy):
    clean_name = name.strip()
    clean_strategy = strategy.strip()
    if not clean_name:
        raise InvalidInputError("Portfolio name cannot be empty")
    if not clean_strategy:
        raise InvalidInputError("Strategy description cannot be empty")
    with database.transaction() as session:
        if portfolio_store.get_portfolio(session, clean_name) is not None:
            raise DuplicateError(f"Portfolio '{clean_name}' already exists")
        portfolio = Portfolio(name=clean_name, strategy=clean_strategy)
        portfolio_store.add_portfolio(session, portfolio)
    logger.info("Created portfolio %s", portfolio.name)
    return portfolio


def find_portfolio(session, name):
    clean_name = name.strip()
    portfolio = portfolio_store.get_portfolio(session, clean_name)
    if portfolio is None:
        raise NotFoundError(f"No portfolio named '{clean_name}'")
    return portfolio


def list_portfolios():
    with database.transaction() as session:
        return portfolio_store.get_all_portfolios(session)


def select_portfolio(name):
    global selected_portfolio
    with database.transaction() as session:
        portfolio = find_portfolio(session, name)
    selected_portfolio = portfolio.name
    logger.info("Selected portfolio %s", portfolio.name)
    return portfolio


def get_selected_portfolio():
    return selected_portfolio


def require_selected_portfolio():
    if selected_portfolio is None:
        raise NoPortfolioSelectedError("No portfolio is currently selected")
    return selected_portfolio


def delete_portfolio(name):
    global selected_portfolio
    with database.transaction() as session:
        portfolio = find_portfolio(session, name)
        holdings, _ = holding_service.calculate_portfolio_positions(session, portfolio)
        if holdings:
            raise PortfolioNotEmptyError(
                f"Cannot delete portfolio '{portfolio.name}' while it still holds shares"
            )
        transaction_store.delete_transactions(session, portfolio)
        portfolio_store.delete_portfolio(session, portfolio)
    if selected_portfolio == portfolio.name:
        selected_portfolio = None
    logger.info("Deleted portfolio %s", portfolio.name)
