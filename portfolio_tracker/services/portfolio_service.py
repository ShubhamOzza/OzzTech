import logging

from portfolio_tracker.errors import (
    DuplicateError,
    InvalidInputError,
    NoPortfolioSelectedError,
    NotFoundError,
    PortfolioNotEmptyError,
)
from portfolio_tracker.models.portfolio import Portfolio
from portfolio_tracker.services import holding_service, transaction_service

logger = logging.getLogger(__name__)

portfolios = {}
selection = {"name": None}


def create_portfolio(name, strategy):
    clean_name = name.strip()
    clean_strategy = strategy.strip()
    if not clean_name:
        raise InvalidInputError("Portfolio name cannot be empty")
    if not clean_strategy:
        raise InvalidInputError("Strategy description cannot be empty")
    if clean_name in portfolios:
        raise DuplicateError(f"Portfolio '{clean_name}' already exists")
    portfolio = Portfolio(clean_name, clean_strategy)
    portfolios[clean_name] = portfolio
    logger.info("Created portfolio %s", portfolio.name)
    return portfolio


def find_portfolio(name):
    clean_name = name.strip()
    try:
        return portfolios[clean_name]
    except KeyError:
        raise NotFoundError(f"No portfolio named '{clean_name}'") from None


def list_portfolios():
    return list(portfolios.values())


def select_portfolio(name):
    portfolio = find_portfolio(name)
    selection["name"] = portfolio.name
    logger.info("Selected portfolio %s", portfolio.name)
    return portfolio


def get_selected_portfolio():
    return selection["name"]


def require_selected_portfolio():
    if selection["name"] is None:
        raise NoPortfolioSelectedError("No portfolio is currently selected")
    return selection["name"]


def delete_portfolio(name):
    portfolio = find_portfolio(name)
    holdings = holding_service.get_holdings(portfolio.name)
    if holdings:
        raise PortfolioNotEmptyError(
            f"Cannot delete portfolio '{portfolio.name}' while it still holds shares"
        )
    transaction_service.clear_transactions(portfolio)
    del portfolios[portfolio.name]
    if selection["name"] == portfolio.name:
        selection["name"] = None
    logger.info("Deleted portfolio %s", portfolio.name)
