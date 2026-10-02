"""
settings.py
Pydantic model for trading configuration files with Hot-Reloading
"""

import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from persistance.connection import SessionLocal, init_db
from persistance.models import TradingConfig

if getattr(sys, "frozen", False):
    DIR = Path(sys.executable).parent
else:
    DIR = Path(__file__).resolve().parent.parent

TRADING_CONFIG_PATH = DIR / "qdata" / "trading_config.json"
TRADING_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── Model ─────────────────────────────────────────────────────────────────────


class TradingConfigPYD(BaseModel):
    model_config = {"from_attributes": True}

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
    """Detects file changes and reloads configuration automatically."""

    def __init__(self, path: Path):
        self.path = path
        self._last_mtime = 0
        self.config = self.reload()
        self.ensure_json_file()

    def ensure_json_file(self):
        init_db()

    def reload(self) -> TradingConfigPYD:
        """Force a reload from disk."""
        init_db()
        try:
            return load_trading_config()
        except FileNotFoundError:
            default_cfg = TradingConfigPYD()
            save_trading_config(default_cfg)
            return default_cfg

    def get_config(self) -> TradingConfigPYD:
        """Returns the config, reloading it only if the file was modified."""
        self.config = self.reload()
        return self.config


# ── Helpers ────────────────────────────────────────────────────────────────────


def _load(path: Path, model: type[BaseModel]) -> BaseModel:
    return model.model_validate_json(path.read_text())


def load_trading_config() -> TradingConfigPYD:
    init_db()
    with SessionLocal() as session:
        row = session.get(TradingConfig, "base")
        if row is None:
            if TRADING_CONFIG_PATH.exists() and TRADING_CONFIG_PATH.stat().st_size:
                legacy = _load(TRADING_CONFIG_PATH, TradingConfigPYD)
                session.close()
                save_trading_config(legacy)
                return legacy
            raise FileNotFoundError("Trading configuration not found in database")
        return TradingConfigPYD.model_validate(row, from_attributes=True)


def save_trading_config(cfg: TradingConfigPYD) -> None:
    init_db()
    with SessionLocal.begin() as session:
        row = session.get(TradingConfig, cfg.name) or TradingConfig(name=cfg.name)
        for key, value in cfg.model_dump().items():
            setattr(row, key, value)
        session.add(row)


# ── Usage ──────────────────────────────────────────────────────────────────────

# Initialize the watcher once
watcher = ConfigWatcher(TRADING_CONFIG_PATH)

# You should call watcher.get_config()
