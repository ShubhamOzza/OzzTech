from decimal import Decimal

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from portfolio_tracker.database import Base


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True)
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2))
