from sqlalchemy import JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_collection, mapped_column

from .connection import Base


class Profiles(Base):
    __tablename__ = "User_Profiles"

    num: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(hash=True)
    configs: Mapped[JSON] = mapped_column()


class GeneralOrders(Base):
    __tablename__ = "general_orders"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    price: Mapped[float] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    side: Mapped[str] = mapped_column()
    symbol: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    time: Mapped[int] = mapped_column(unique=True)
    previous_time: Mapped[int] = mapped_column(unique=True)
    fees: Mapped[float] = mapped_column()


class TakeStopOrders(Base):
    __tablename__ = "take_stop_orders"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    price: Mapped[float] = mapped_column(nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    side: Mapped[str] = mapped_column()
    symbol: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column()
    time: Mapped[int] = mapped_column(unique=True)
    previous_time: Mapped[int] = mapped_column(unique=True)
    fees: Mapped[float] = mapped_column()


class Results(Base):
    __tablename__ = "Results"

    order_entry: Mapped[JSON] = mapped_column()
    order_exit: Mapped[JSON] = mapped_column()
    profit: Mapped[int] = mapped_column()
    loss: Mapped[int] = mapped_column()
    date: Mapped[str] = mapped_column()
