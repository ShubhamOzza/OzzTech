class Transaction:
    def __init__(self, portfolio, asset, side, quantity, price_per_share):
        self.portfolio = portfolio
        self.asset = asset
        self.side = side
        self.quantity = quantity
        self.price_per_share = price_per_share
