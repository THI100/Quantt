from typing import Optional

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .connection import Base

# class UserProfile(Base):
#     __tablename__ = "user_profiles"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(50), unique=True)
#     password: Mapped[str] = mapped_column(String(255))
#     configs: Mapped[JSON] = mapped_column(JSON, nullable=True)
#     orders: Mapped[list["GeneralOrder"]] = relationship(back_populates="user")


class GeneralOrder(Base):
    __tablename__ = "general_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    # user_id: Mapped[int] = mapped_column(ForeignKey("user_profiles.id"))
    # user: Mapped["UserProfile"] = relationship(back_populates="orders")
    # take_order_list: Mapped[list["TakeStopOrder"]] = relationship(back_populates="parent_order")
    price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    side: Mapped[str] = mapped_column(String(10))
    symbol: Mapped[str] = mapped_column(String(20))
    order_type: Mapped[str] = mapped_column(String(20))
    time: Mapped[int] = mapped_column(unique=True)
    previous_time: Mapped[int] = mapped_column(nullable=True)
    # Foreign Keys to TakeStopOrders
    take_id: Mapped[Optional[int]] = mapped_column(ForeignKey("take_stop_orders.id"))
    stop_id: Mapped[Optional[int]] = mapped_column(ForeignKey("take_stop_orders.id"))
    # Relationships
    take_order: Mapped[Optional["TakeStopOrder"]] = relationship(foreign_keys=[take_id])
    stop_order: Mapped[Optional["TakeStopOrder"]] = relationship(foreign_keys=[stop_id])


class TakeStopOrder(Base):
    __tablename__ = "take_stop_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_order_id: Mapped[int] = mapped_column(ForeignKey("general_orders.id"))
    # parent_order: Mapped["GeneralOrder"] = relationship(back_populates="take_order_list")
    price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    side: Mapped[str] = mapped_column(String(10))
    symbol: Mapped[str] = mapped_column(String(20))
    order_type: Mapped[str] = mapped_column(String(30))  # Exchange order type
    time: Mapped[int] = mapped_column(unique=True)
    fees: Mapped[float] = mapped_column(Float, default=0.0)


class Result(Base):
    __tablename__ = "results"

    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    # Foreign ids for profits, losses and referent orders
    entry_order_id: Mapped[int] = mapped_column(ForeignKey("general_orders.id"))
    exit_order_id: Mapped[int] = mapped_column(ForeignKey("take_stop_orders.id"))
    profit_loss: Mapped[Optional[float]] = mapped_column(Float)
    date: Mapped[Optional[str]] = mapped_column(String(30))
    entry_order: Mapped["GeneralOrder"] = relationship(foreign_keys=[entry_order_id])
