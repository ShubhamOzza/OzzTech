from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from portfolio_tracker.database import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    strategy: Mapped[str] = mapped_column(String(255))
