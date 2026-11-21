from datetime import date
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from portfolio_tracker.database import Base
from portfolio_tracker.models.asset import Asset
from portfolio_tracker.models.portfolio import Portfolio


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id"))
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    side: Mapped[str] = mapped_column(Enum("buy", "sell"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    price_per_share: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    trade_date: Mapped[date]

    portfolio: Mapped[Portfolio] = relationship()
    asset: Mapped[Asset] = relationship(lazy="selectin")
