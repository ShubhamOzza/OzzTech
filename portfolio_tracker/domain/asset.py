class Asset:
    # Prices are stored in PricingService instead of here so a live market
    # feed can be plugged in later without changing Asset.
    def __init__(self, ticker: str, name: str):
        self.ticker = ticker
        self.name = name
