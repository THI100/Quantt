"""
config_models.py
Pydantic models for trading configuration files + FastAPI routes to read/update them via API.
"""

from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import select

from persistance.connection import SessionLocal, ensure_config_schema
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

    def __init__(self, profile_name: str = "base"):
        self.profile_name = profile_name
        self.config = RiskConfigPYD(name=profile_name)

    def reload(self) -> RiskConfigPYD:
        """Reload the configuration from SQLite."""
        try:
            return load_risk_config(self.profile_name)
        except FileNotFoundError:
            default_cfg = RiskConfigPYD(name=self.profile_name)
            error = save_risk_config(default_cfg)
            if error:
                raise RuntimeError(error)
            return default_cfg

    def get_config(self) -> RiskConfigPYD:
        """Return the latest configuration stored in SQLite."""
        self.config = self.reload()
        return self.config


# ── Helpers ────────────────────────────────────────────────────────────────────


# Convenience accessors
def load_risk_config(profile_name: str = "base") -> RiskConfigPYD:
    ensure_config_schema()
    session = SessionLocal()
    try:
        row = session.get(RiskConfig, profile_name)
        if row is None:
            raise FileNotFoundError(
                f"Risk configuration profile '{profile_name}' not found"
            )
        return RiskConfigPYD.model_validate(row, from_attributes=True)
    except FileNotFoundError:
        raise
    except Exception as exc:
        session.rollback()
        raise RuntimeError(
            f"Failed to load risk configuration profile '{profile_name}': {exc}"
        ) from exc
    finally:
        session.close()


def save_risk_config(cfg: RiskConfigPYD) -> str | None:
    try:
        ensure_config_schema()
    except Exception as exc:
        return f"Failed to prepare risk configuration schema: {exc}"
    session = SessionLocal()
    try:
        row = session.get(RiskConfig, cfg.name) or RiskConfig(name=cfg.name)
        for key, value in cfg.model_dump().items():
            setattr(row, key, value)
        session.add(row)
        session.commit()
        return None
    except Exception as exc:
        session.rollback()
        return f"Failed to save risk configuration profile '{cfg.name}': {exc}"
    finally:
        session.close()


def delete_risk_config(profile_name: str) -> str | None:
    try:
        ensure_config_schema()
    except Exception as exc:
        return f"Failed to prepare risk configuration schema: {exc}"
    session = SessionLocal()
    try:
        row = session.get(RiskConfig, profile_name)
        if row is None:
            return f"Risk configuration profile '{profile_name}' not found"
        session.delete(row)
        session.commit()
        return None
    except Exception as exc:
        session.rollback()
        return f"Failed to delete risk configuration profile '{profile_name}': {exc}"
    finally:
        session.close()


def list_risk_profiles() -> list[str]:
    ensure_config_schema()
    session = SessionLocal()
    try:
        return list(session.scalars(select(RiskConfig.name).order_by(RiskConfig.name)))
    except Exception as exc:
        session.rollback()
        raise RuntimeError(f"Failed to list risk profiles: {exc}") from exc
    finally:
        session.close()


# ── Usage ──────────────────────────────────────────────────────────────────────

# Initialize the watcher once
watcher = ConfigWatcher()

# You should call watcher.get_config()
