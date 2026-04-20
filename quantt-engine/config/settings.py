"""
settings.py
Pydantic model for trading configuration files
"""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

# ── Paths ──────────────────────────────────────────────────────────────────────
CONFIG_DIR = Path(__file__).parent  # adjust if configs live elsewhere
TRADING_CONFIG_PATH = CONFIG_DIR / "trading_config.json"

# ── Model ─────────────────────────────────────────────────────────────────────


class TradingConfig(BaseModel):
    is_demo_enabled: bool = True
    timeframe: str = "15m"
    exchange: str = "binance"
    future_spot: Literal["future", "spot"] = "future"
    list_of_interest: list[str] = [
        "BTC/USDT",
        "ETH/USDT",
        "BNB/USDT",
        "XRP/USDT",
        "ADA/USDT",
        "AVAX/USDT",
        "ETC/USDT",
        "LINK/USDT",
    ]  # Field(default_factory=list)
    list_of_params: list[str] = [
        "MACD",
        "RSI",
        "SMR",
        "TnK",
        "EMA",
        "ATR",
        "DSCP",
        "SMR",
    ] # Field(default_factory=list)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _load(path: Path, model: type[BaseModel]) -> BaseModel:
    """Load a JSON file into a Pydantic model."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    return model.model_validate_json(path.read_text())


def _save(path: Path, instance: BaseModel) -> None:
    """Persist a Pydantic model back to its JSON file."""
    path.write_text(instance.model_dump_json(indent=2))


# Convenience accessors
def load_trading_config() -> TradingConfig:
    return _load(TRADING_CONFIG_PATH, TradingConfig)


def save_trading_config(cfg: TradingConfig) -> None:
    _save(TRADING_CONFIG_PATH, cfg)
