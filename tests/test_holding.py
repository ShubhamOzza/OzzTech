from decimal import Decimal

from portfolio_tracker.models.asset import Asset
from portfolio_tracker.models.holding import Holding

APPLE = Asset(ticker="AAPL", name="Apple Inc.")


def test_market_value_is_quantity_times_current_price():
    holding = Holding(
        APPLE,
        quantity=Decimal("10"),
        average_cost=Decimal("150"),
        current_price=Decimal("170"),
    )

    assert holding.market_value == Decimal("1700")


def test_unrealized_gain_compares_current_price_to_average_cost():
    holding = Holding(
        APPLE,
        quantity=Decimal("10"),
        average_cost=Decimal("150"),
        current_price=Decimal("170"),
    )

    assert holding.unrealized_gain == Decimal("200")


def test_unrealized_loss_is_negative():
    holding = Holding(
        APPLE,
        quantity=Decimal("10"),
        average_cost=Decimal("150"),
        current_price=Decimal("140"),
    )

    assert holding.unrealized_gain == Decimal("-100")


def test_no_current_price_means_no_market_value_or_gain():
    holding = Holding(
        APPLE,
        quantity=Decimal("10"),
        average_cost=Decimal("150"),
        current_price=None,
    )

    assert holding.market_value is None
    assert holding.unrealized_gain is None
