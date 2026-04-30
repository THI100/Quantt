from typing import Optional

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .connection import Base


class GeneralOrder(Base):
    __tablename__ = "general_orders"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    entrance_exit: Mapped[str] = mapped_column(String(10))
    price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    side: Mapped[str] = mapped_column(String(10))
    symbol: Mapped[str] = mapped_column(String(20))
    order_type: Mapped[str] = mapped_column(String(20))
    time: Mapped[str] = mapped_column(String(32))
    previous_time: Mapped[str] = mapped_column(String(32), nullable=True)
    # Foreign Keys to TakeStopOrders
    take_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("take_stop_orders.id")
    )
    stop_id: Mapped[Optional[str]] = mapped_column(
        String(32), ForeignKey("take_stop_orders.id")
    )
    # Relationships
    take_order: Mapped[Optional["TakeStopOrder"]] = relationship(foreign_keys=[take_id])
    stop_order: Mapped[Optional["TakeStopOrder"]] = relationship(foreign_keys=[stop_id])


class TakeStopOrder(Base):
    __tablename__ = "take_stop_orders"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    parent_order_id: Mapped[int] = mapped_column(ForeignKey("general_orders.id"))
    price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    side: Mapped[str] = mapped_column(String(10))
    symbol: Mapped[str] = mapped_column(String(20))
    order_type: Mapped[str] = mapped_column(String(30))  # Exchange order type
    time: Mapped[str] = mapped_column(String(32), unique=True)
    fees: Mapped[float] = mapped_column(Float, default=0.0)
