class PortfolioTrackerError(Exception):
    """Base exception for expected errors in the portfolio tracker."""


class InvalidInputError(PortfolioTrackerError):
    """Raised when CLI input cannot be parsed or menu choice is invalid."""


class ValidationError(PortfolioTrackerError):
    """Raised when an input value breaks a validation rule."""


class InvalidTickerError(ValidationError):
    pass


class InvalidNameError(ValidationError):
    pass


class InvalidAmountError(ValidationError):
    pass


class InvalidPriceError(ValidationError):
    pass


class InvalidQuantityError(ValidationError):
    pass


class DuplicateError(PortfolioTrackerError):
    """Raised when trying to create an item that already exists."""


class DuplicateAssetError(DuplicateError):
    def __init__(self, ticker: str):
        self.ticker = ticker
        super().__init__(f"Asset with ticker '{ticker}' already exists.")


class DuplicatePortfolioError(DuplicateError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"A portfolio named '{name}' already exists.")


class NotFoundError(PortfolioTrackerError):
    """Raised when a requested item cannot be found."""


class AssetNotFoundError(NotFoundError):
    def __init__(self, ticker: str):
        self.ticker = ticker
        super().__init__(f"No asset found with ticker '{ticker}'.")


class PortfolioNotFoundError(NotFoundError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"No portfolio found with name '{name}'.")


class NoPortfolioSelectedError(PortfolioTrackerError):
    def __init__(self):
        super().__init__(
            "No portfolio is currently selected. Please select a portfolio first."
        )


class PortfolioNotEmptyError(PortfolioTrackerError):
    def __init__(self, name: str, tickers: list[str]):
        self.name = name
        self.tickers = tickers
        held_list = ", ".join(tickers)
        super().__init__(
            f"Cannot delete portfolio '{name}' while it still holds shares ({held_list}). "
            "Sell all positions first."
        )


class InsufficientFundsError(PortfolioTrackerError):
    def __init__(self, required: float, available: float):
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient cash: purchase costs ${required:,.2f}, "
            f"but your cash balance is ${available:,.2f}."
        )


class InsufficientSharesError(PortfolioTrackerError):
    def __init__(self, ticker: str, requested: int, available: int, portfolio_name: str):
        self.ticker = ticker
        self.requested = requested
        self.available = available
        self.portfolio_name = portfolio_name
        super().__init__(
            f"Cannot sell {requested} shares of {ticker} from '{portfolio_name}' "
            f"(currently holding {available} shares)."
        )
