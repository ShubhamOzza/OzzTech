import logging
import math

from portfolio_tracker.domain.account import CashAccount
from portfolio_tracker.errors import InsufficientFundsError, InvalidAmountError

logger = logging.getLogger(__name__)


class CashService:
    def __init__(self):
        self._account = CashAccount()

    def get_balance(self) -> float:
        return self._account.balance

    def deposit(self, amount: float) -> float:
        if math.isnan(amount) or math.isinf(amount) or amount <= 0:
            raise InvalidAmountError("Deposit amount must be greater than zero.")

        # Round to 8 decimal places to avoid float drift like 0.1 + 0.2 != 0.3
        self._account.balance = round(self._account.balance + amount, 8)
        logger.info(
            "Deposited %.2f; cash balance is now %.2f",
            amount,
            self._account.balance,
        )
        return self._account.balance

    def deduct_cash(self, cost: float) -> float:
        if math.isnan(cost) or math.isinf(cost) or cost <= 0:
            raise InvalidAmountError("Purchase cost must be greater than zero.")
        if cost > self._account.balance:
            raise InsufficientFundsError(cost, self._account.balance)

        self._account.balance = round(self._account.balance - cost, 8)
        return self._account.balance

    def add_cash(self, proceeds: float) -> float:
        if math.isnan(proceeds) or math.isinf(proceeds) or proceeds < 0:
            raise InvalidAmountError("Sale proceeds cannot be negative.")

        self._account.balance = round(self._account.balance + proceeds, 8)
        return self._account.balance
