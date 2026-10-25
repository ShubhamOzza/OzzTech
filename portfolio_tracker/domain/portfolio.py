class Position:
    def __init__(self, ticker: str, quantity: int, average_cost: float):
        self.ticker = ticker
        self.quantity = quantity
        self.average_cost = average_cost


class Trade:
    def __init__(
        self,
        trade_type: str,
        ticker: str,
        quantity: int,
        price: float,
        total: float,
        realized_gain: float | None = None,
    ):
        self.trade_type = trade_type
        self.ticker = ticker
        self.quantity = quantity
        self.price = price
        self.total = total
        self.realized_gain = realized_gain


class Portfolio:
    def __init__(self, name: str, strategy: str):
        self.name = name
        self.strategy = strategy
        self.positions: dict[str, Position] = {}
        self.trades: list[Trade] = []
        self.realized_gain = 0.0
