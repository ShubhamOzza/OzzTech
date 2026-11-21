class Holding:
    def __init__(self, asset, quantity, average_cost, current_price):
        self.asset = asset
        self.quantity = quantity
        self.average_cost = average_cost
        self.current_price = current_price

    @property
    def market_value(self):
        if self.current_price is None:
            return None
        return self.quantity * self.current_price

    @property
    def unrealized_gain(self):
        if self.current_price is None:
            return None
        return (self.current_price - self.average_cost) * self.quantity
