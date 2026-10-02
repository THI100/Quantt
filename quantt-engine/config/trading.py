"""
settings.py
Pydantic model for trading configuration files with Hot-Reloading
"""

from typing import Literal

from pydantic import BaseModel, Field

from persistance.connection import SessionLocal
from persistance.models import TradingConfig

# ── Model ─────────────────────────────────────────────────────────────────────


class TradingConfigPYD(BaseModel):
    name: str = "base"
    is_demo_enabled: bool = True
    timeframe: str = "15m"
    exchange: Literal[
        "binance", "bybit", "okx", "mexc", "aster", "dydx", "hyperliquid", "lighter"
    ] = "binance"
    execution_order: Literal["market", "limit"] = "limit"
    future_spot: Literal["future", "spot"] = "spot"
    list_of_interest: list[str] = Field(
        default_factory=lambda: [
            "BTC/USDT",
            "ETH/USDT",
            "BNB/USDT",
            "XRP/USDT",
            "ADA/USDT",
            "AVAX/USDT",
            "ETC/USDT",
            "LINK/USDT",
        ]
    )
    list_of_parameters: list[str] = Field(
        default_factory=lambda: ["RSI", "SMR", "TnK", "EMA", "ATR", "DSCP"]
    )


# ── Watcher Logic ─────────────────────────────────────────────────────────────


class ConfigWatcher:
    """Reads the latest configuration from SQLite."""

    def __init__(self, path=None):
        self.path = path
        self.config = self.reload()

    def reload(self) -> TradingConfigPYD:
        """Reload the configuration from SQLite."""
        try:
            return load_trading_config()
        except FileNotFoundError:
            default_cfg = TradingConfigPYD()
            save_trading_config(default_cfg)
            return default_cfg

    def get_config(self) -> TradingConfigPYD:
        """Return the latest configuration stored in SQLite."""
        self.config = self.reload()
        return self.config


# ── Helpers ────────────────────────────────────────────────────────────────────


def load_trading_config() -> TradingConfigPYD:
    with SessionLocal() as session:
        row = session.get(TradingConfig, "base")
        if row is None:
            raise FileNotFoundError("Trading configuration not found in database")
        return TradingConfigPYD.model_validate(row, from_attributes=True)


def save_trading_config(cfg: TradingConfigPYD) -> None:
    with SessionLocal.begin() as session:
        row = session.get(TradingConfig, cfg.name) or TradingConfig(name=cfg.name)
        for key, value in cfg.model_dump().items():
            setattr(row, key, value)
        session.add(row)


# ── Usage ──────────────────────────────────────────────────────────────────────

# Initialize the watcher once
watcher = ConfigWatcher()

# You should call watcher.get_config()
