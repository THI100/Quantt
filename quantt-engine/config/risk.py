"""
config_models.py
Pydantic models for trading configuration files + FastAPI routes to read/update them via API.
"""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

# ── Paths ──────────────────────────────────────────────────────────────────────

CONFIG_DIR = Path(__file__).parent  # adjust if configs live elsewhere
RISK_CONFIG_PATH = CONFIG_DIR / "risk_config.json"

# ── Models ─────────────────────────────────────────────────────────────────────


class RiskConfig(BaseModel):
    risk_reward_ratio: float = 2.0
    acceptable_confidence: int = 40  # Field(40, ge=0, le=100)
    atr_multiplier: float = 0.4
    maximum_loss: float = 0.15  # Field(0.15, gt=0, le=1)
    percentage_of_capital_per_trade: float = 0.02  # Field(0.02, gt=0, le=1)
    leverage: int = 50  # Field(50, ge=1)
    cross_isolated: Literal["cross", "isolated"] = "cross"


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
def load_risk_config() -> RiskConfig:
    return _load(RISK_CONFIG_PATH, RiskConfig)


def save_risk_config(cfg: RiskConfig) -> None:
    _save(RISK_CONFIG_PATH, cfg)
