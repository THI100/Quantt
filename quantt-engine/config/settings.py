"""
settings.py
Pydantic model for trading configuration files with Hot-Reloading
"""

import json
import time
from pathlib import Path
from typing import Literal

from loguru import logger
from pydantic import BaseModel, Field

# ── Paths ──────────────────────────────────────────────────────────────────────
CONFIG_DIR = Path(__file__).parent
TRADING_CONFIG_PATH = CONFIG_DIR / "trading_config.json"

# ── Model ─────────────────────────────────────────────────────────────────────


class TradingConfig(BaseModel):
    is_demo_enabled: bool = True
    timeframe: str = "15m"
    exchange: Literal["binance", "bybit", "okx", "mexc"] = "binance"
    execution_order: Literal["market", "limit"] = "limit"
    future_spot: Literal["future", "spot"] = "future"
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

    def reload(self) -> TradingConfig:
        """Force a reload from disk."""
        if not self.path.exists():
            # If file doesn't exist, save defaults to create it
            default_cfg = TradingConfig()
            save_trading_config(default_cfg)
            return default_cfg

        self._last_mtime = self.path.stat().st_mtime
        return load_trading_config()

    def get_config(self) -> TradingConfig:
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


def load_trading_config() -> TradingConfig:
    return _load(TRADING_CONFIG_PATH, TradingConfig)


def save_trading_config(cfg: TradingConfig) -> None:
    _save(TRADING_CONFIG_PATH, cfg)


# ── Usage ──────────────────────────────────────────────────────────────────────

# Initialize the watcher once
watcher = ConfigWatcher(TRADING_CONFIG_PATH)

# You should call watcher.get_config()
