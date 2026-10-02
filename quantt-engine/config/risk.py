"""
config_models.py
Pydantic models for trading configuration files + FastAPI routes to read/update them via API.
"""

from typing import Literal

from pydantic import BaseModel, Field

from persistance.connection import SessionLocal
from persistance.models import RiskConfig

# ── Models ─────────────────────────────────────────────────────────────────────


class RiskConfigPYD(BaseModel):
    name: str = "base"
    risk_reward_ratio: float = Field(default=2.0, ge=0, le=10)
    acceptable_confidence: int = Field(default=40, ge=0, le=100)
    atr_multiplier: float = 0.4
    maximum_loss: float = Field(default=0.15, gt=0, le=1)  # Still
    percentage_of_capital_per_trade: float = Field(default=0.02, gt=0, le=1)
    leverage: int = Field(default=50, ge=1, le=100)
    maximum_iceberg_share: float = Field(default=0.02, gt=0, le=0.1)
    cross_isolated: Literal["cross", "isolated"] = "cross"


# ── Watcher Logic ─────────────────────────────────────────────────────────────


class ConfigWatcher:
    """Reads the latest configuration from SQLite."""

    def __init__(self, path=None):
        self.path = path
        self.config = self.reload()

    def reload(self) -> RiskConfigPYD:
        """Reload the configuration from SQLite."""
        try:
            return load_risk_config()
        except FileNotFoundError:
            default_cfg = RiskConfigPYD()
            save_risk_config(default_cfg)
            return default_cfg

    def get_config(self) -> RiskConfigPYD:
        """Return the latest configuration stored in SQLite."""
        self.config = self.reload()
        return self.config


# ── Helpers ────────────────────────────────────────────────────────────────────


# Convenience accessors
def load_risk_config() -> RiskConfigPYD:
    with SessionLocal() as session:
        row = session.get(RiskConfig, "base")
        if row is None:
            raise FileNotFoundError("Risk configuration not found in database")
        return RiskConfigPYD.model_validate(row, from_attributes=True)


def save_risk_config(cfg: RiskConfigPYD) -> None:
    with SessionLocal.begin() as session:
        row = session.get(RiskConfig, cfg.name) or RiskConfig(name=cfg.name)
        for key, value in cfg.model_dump().items():
            setattr(row, key, value)
        session.add(row)


# ── Usage ──────────────────────────────────────────────────────────────────────

# Initialize the watcher once
watcher = ConfigWatcher()

# You should call watcher.get_config()
