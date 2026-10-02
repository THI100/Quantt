"""
settings.py
Pydantic model for trading configuration files with Hot-Reloading
"""

import os

# ── Paths ──────────────────────────────────────────────────────────────────────
import sys
from pathlib import Path
from typing import Literal

from loguru import logger
from pydantic import BaseModel, Field

from persistance.connection import SessionLocal
from persistance.models import TradingConfig

if getattr(sys, "frozen", False):
    DIR = Path(sys.executable).parent
else:
    DIR = Path(__file__).resolve().parent.parent

TRADING_CONFIG_PATH = DIR / "qdata" / "trading_config.json"
TRADING_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

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
    """Detects file changes and reloads configuration automatically."""

    def __init__(self, path: Path):
        self.path = path
        self._last_mtime = 0
        self.config = self.reload()
        self.ensure_json_file()

    def ensure_json_file(self, fpath=TRADING_CONFIG_PATH):
        fpath.parent.mkdir(parents=True, exist_ok=True)

        if not os.path.exists(fpath):
            with open(fpath, "w") as f:
                f.write("")
            return logger.info(f"Created file: {fpath}")

    def reload(self) -> TradingConfigPYD:
        """Force a reload from disk."""
        if not self.path.exists():
            # If file doesn't exist, save defaults to create it
            default_cfg = TradingConfigPYD()
            save_trading_config(default_cfg)
            return default_cfg

        self._last_mtime = self.path.stat().st_mtime
        return load_trading_config()

    def get_config(self) -> TradingConfigPYD:
        """Returns the config, reloading it only if the file was modified."""
        current_mtime = self.path.stat().st_mtime
        if current_mtime > self._last_mtime:
            logger.debug(f"Config change detected! Reloading {self.path.name}...")
            self.config = self.reload()
        return self.config


# ── Helpers ────────────────────────────────────────────────────────────────────


def _load(path: Path, model: type[BaseModel]) -> BaseModel:
    return model.model_validate_json(path.read_text())


def _save(path: Path, instance: BaseModel) -> None:
    path.write_text(instance.model_dump_json(indent=2))


def load_trading_config() -> TradingConfigPYD:
    return _load(TRADING_CONFIG_PATH, TradingConfigPYD)


def save_trading_config(cfg: TradingConfigPYD) -> None:
    _save(TRADING_CONFIG_PATH, cfg)


# ── Usage ──────────────────────────────────────────────────────────────────────

# Initialize the watcher once
watcher = ConfigWatcher(TRADING_CONFIG_PATH)

# You should call watcher.get_config()
