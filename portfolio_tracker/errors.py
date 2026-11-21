class TrackerError(Exception):
    """Base class for every business rule the tracker enforces."""


class DuplicateError(TrackerError):
    """Something with this name or ticker already exists."""


class NotFoundError(TrackerError):
    """No portfolio or asset with this name or ticker exists."""


class InvalidAmountError(TrackerError):
    """A quantity, price, or cash amount is out of range."""


class InvalidInputError(TrackerError):
    """A required text value is empty or invalid."""


class InsufficientFundsError(TrackerError):
    """The account does not have enough cash for this purchase."""


class InsufficientSharesError(TrackerError):
    """The portfolio does not hold enough shares for this sale."""


class NoPortfolioSelectedError(TrackerError):
    """An operation requires a selected portfolio, but none is selected."""


class PortfolioNotEmptyError(TrackerError):
    """A portfolio still holds shares and cannot be deleted."""
