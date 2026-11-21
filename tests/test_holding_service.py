from decimal import Decimal

from portfolio_tracker.services import (
    asset_service,
    holding_service,
    portfolio_service,
    price_service,
    transaction_service,
)


def test_holdings_are_valued_at_the_current_price(funded_portfolio, monkeypatch):
    # A stand-in price source: the test decides the price, not the market.
    monkeypatch.setattr(price_service, "get_price", lambda ticker: Decimal("150"))
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("110"))

    [holding] = holding_service.get_holdings(funded_portfolio)

    assert holding.market_value == Decimal("600")
    assert holding.unrealized_gain == Decimal("160")


def test_multiple_buys_recalculate_weighted_average_cost(funded_portfolio):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("2"), Decimal("100"))
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("3"), Decimal("150"))

    [holding] = holding_service.get_holdings(funded_portfolio)

    assert holding.quantity == Decimal("5")
    assert holding.average_cost == Decimal("130")


def test_partial_sell_reduces_quantity_and_keeps_average_cost_unchanged(
    funded_portfolio,
):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("2"), Decimal("160"))

    transaction_service.sell(funded_portfolio, "AAPL", Decimal("3"), Decimal("150"))

    [holding] = holding_service.get_holdings(funded_portfolio)
    assert holding.quantity == Decimal("3")
    assert holding.average_cost == Decimal("120")


def test_fully_sold_position_is_removed_from_holdings_while_realized_gain_remains(
    funded_portfolio,
):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))
    transaction_service.sell(funded_portfolio, "AAPL", Decimal("4"), Decimal("125"))

    summary = holding_service.get_portfolio_summary(funded_portfolio)

    assert summary["holdings"] == []
    assert summary["realized_gain"] == Decimal("100")


def test_realized_loss_is_negative_when_sold_below_average_cost(funded_portfolio):
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("5"), Decimal("100"))
    transaction_service.sell(funded_portfolio, "AAPL", Decimal("2"), Decimal("80"))

    summary = holding_service.get_portfolio_summary(funded_portfolio)

    assert summary["realized_gain"] == Decimal("-40")


def test_positions_in_different_portfolios_are_independent(funded_portfolio):
    portfolio_service.create_portfolio("Dividend income", "Dividend stocks")
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))
    transaction_service.buy("Dividend income", "AAPL", Decimal("2"), Decimal("200"))

    [tech_holding] = holding_service.get_holdings(funded_portfolio)
    [div_holding] = holding_service.get_holdings("Dividend income")

    assert tech_holding.quantity == Decimal("4")
    assert tech_holding.average_cost == Decimal("100")
    assert div_holding.quantity == Decimal("2")
    assert div_holding.average_cost == Decimal("200")


def test_portfolio_summary_totals_market_value_and_gains(funded_portfolio, monkeypatch):
    asset_service.add_asset("MSFT", "Microsoft Corp.")
    prices = {"AAPL": Decimal("150"), "MSFT": Decimal("220")}
    monkeypatch.setattr(price_service, "get_price", lambda ticker: prices[ticker])

    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))
    transaction_service.sell(funded_portfolio, "AAPL", Decimal("1"), Decimal("130"))
    transaction_service.buy(funded_portfolio, "MSFT", Decimal("2"), Decimal("200"))

    summary = holding_service.get_portfolio_summary(funded_portfolio)

    assert summary["total_market_value"] == Decimal("890")
    assert summary["total_unrealized_gain"] == Decimal("190")
    assert summary["realized_gain"] == Decimal("30")


def test_portfolio_summary_handles_unpriced_asset_without_crashing(
    funded_portfolio, monkeypatch
):
    monkeypatch.setattr(price_service, "get_price", lambda ticker: None)
    transaction_service.buy(funded_portfolio, "AAPL", Decimal("4"), Decimal("100"))

    summary = holding_service.get_portfolio_summary(funded_portfolio)

    [holding] = summary["holdings"]
    assert holding.market_value is None
    assert holding.unrealized_gain is None
    assert summary["total_market_value"] == Decimal("0")
    assert summary["total_unrealized_gain"] == Decimal("0")
