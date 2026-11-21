current_prices = {}


def set_price(ticker, price):
    current_prices[ticker] = price


def get_price(ticker):
    return current_prices.get(ticker)
