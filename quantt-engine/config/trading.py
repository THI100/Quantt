"""
settings.py
Pydantic model for trading configuration files with Hot-Reloading
"""

from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import select

from persistance.connection import SessionLocal, ensure_config_schema
from persistance.models import TradingConfig

# ── Model ─────────────────────────────────────────────────────────────────────


class TradingConfigPYD(BaseModel):
    name: str = "base"
    is_demo_enabled: bool = True
    timeframe: str = "15m"
    exchange: Literal[
        "binance",
        "bybit",
        "okx",
        "mexc",
        "aster",
        "dydx",
        "hyperliquid",
        "lighter",
        "NULL",
    ] = "NULL"
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

    def __init__(self, profile_name: str = "base"):
        self.profile_name = profile_name
        self.config = TradingConfigPYD(name=profile_name)

    def reload(self) -> TradingConfigPYD:
        """Reload the configuration from SQLite."""
        try:
            return load_trading_config(self.profile_name)
        except FileNotFoundError:
            default_cfg = TradingConfigPYD(name=self.profile_name)
            error = save_trading_config(default_cfg)
            if error:
                raise RuntimeError(error)
            return default_cfg

    def get_config(self) -> TradingConfigPYD:
        """Return the latest configuration stored in SQLite."""
        self.config = self.reload()
        return self.config


# ── Helpers ────────────────────────────────────────────────────────────────────


def load_trading_config(profile_name: str = "base") -> TradingConfigPYD:
    ensure_config_schema()
    session = SessionLocal()
    try:
        row = session.get(TradingConfig, profile_name)
        if row is None:
            raise FileNotFoundError(
                f"Trading configuration profile '{profile_name}' not found"
            )
        return TradingConfigPYD.model_validate(row, from_attributes=True)
    except FileNotFoundError:
        raise
    except Exception as exc:
        session.rollback()
        raise RuntimeError(
            f"Failed to load trading configuration profile '{profile_name}': {exc}"
        ) from exc
    finally:
        session.close()


def save_trading_config(cfg: TradingConfigPYD) -> str | None:
    try:
        ensure_config_schema()
    except Exception as exc:
        return f"Failed to prepare trading configuration schema: {exc}"
    session = SessionLocal()
    try:
        row = session.get(TradingConfig, cfg.name) or TradingConfig(name=cfg.name)
        for key, value in cfg.model_dump().items():
            setattr(row, key, value)
        session.add(row)
        session.commit()
        return None
    except Exception as exc:
        session.rollback()
        return f"Failed to save trading configuration profile '{cfg.name}': {exc}"
    finally:
        session.close()


def delete_trading_config(profile_name: str) -> str | None:
    try:
        ensure_config_schema()
    except Exception as exc:
        return f"Failed to prepare trading configuration schema: {exc}"
    session = SessionLocal()
    try:
        row = session.get(TradingConfig, profile_name)
        if row is None:
            return f"Trading configuration profile '{profile_name}' not found"
        session.delete(row)
        session.commit()
        return None
    except Exception as exc:
        session.rollback()
        return f"Failed to delete trading configuration profile '{profile_name}': {exc}"
    finally:
        session.close()


def list_trading_profiles() -> list[str]:
    ensure_config_schema()
    session = SessionLocal()
    try:
        return list(
            session.scalars(select(TradingConfig.name).order_by(TradingConfig.name))
        )
    except Exception as exc:
        session.rollback()
        raise RuntimeError(f"Failed to list trading profiles: {exc}") from exc
    finally:
        session.close()


# ── Usage ──────────────────────────────────────────────────────────────────────

# Initialize the watcher once
watcher = ConfigWatcher()

# You should call watcher.get_config()
