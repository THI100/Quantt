from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from .connection import Base


class Profiles(Base):
    __tablename__ = "User_Profiles"

    num: Mapped[int] = mapped_column(primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(unique=True)
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
