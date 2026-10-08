from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
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
    exchange: Mapped[str] = mapped_column(
        String(16), ForeignKey("trading_config.exchange")
    )
    # Relationships
    take_order: Mapped[Optional["TakeStopOrder"]] = relationship(foreign_keys=[take_id])
    stop_order: Mapped[Optional["TakeStopOrder"]] = relationship(foreign_keys=[stop_id])
    exchange_origin: Mapped["TradingConfig"] = relationship(foreign_keys=[exchange])


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


class TradingConfig(Base):
    __tablename__ = "trading_config"

    name: Mapped[str] = mapped_column(String(32), primary_key=True)
    is_demo_enabled: Mapped[bool] = mapped_column(Boolean)
    timeframe: Mapped[str] = mapped_column(String(8))
    exchange: Mapped[str] = mapped_column(String(16))
    execution_order: Mapped[str] = mapped_column(String(8))
    future_spot: Mapped[str] = mapped_column(String(8))
    list_of_interest: Mapped[list[str]] = mapped_column(JSON)
    list_of_parameters: Mapped[list[str]] = mapped_column(JSON)


class RiskConfig(Base):
    __tablename__ = "risk_config"

    name: Mapped[str] = mapped_column(String(32), primary_key=True)
    risk_reward_ratio: Mapped[float] = mapped_column(Float, default=2.0)
    acceptable_confidence: Mapped[int] = mapped_column(Integer, default=50)
    atr_multiplier: Mapped[float] = mapped_column(Float, default=2.0)
    maximum_loss: Mapped[float] = mapped_column(Float, default=0.1)
    percentage_of_capital_per_trade: Mapped[float] = mapped_column(Float, default=0.02)
    leverage: Mapped[int] = mapped_column(Integer, default=10)
    maximum_iceberg_share: Mapped[float] = mapped_column(Float, default=0.02)
    cross_isolated: Mapped[str] = mapped_column(String(10))


class Store(Base):
    __tablename__ = "store"

    exchange: Mapped[str] = mapped_column(String(16), primary_key=True)
    data: Mapped[datetime] = mapped_column(DateTime)
    balance_dt: Mapped[float] = mapped_column(Float, default=0.0)
    balance_dc: Mapped[float] = mapped_column(Float, default=0.0)
