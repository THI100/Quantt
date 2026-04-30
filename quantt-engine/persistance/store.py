"""
store.py
Pydantic model for Storing misc variables.
"""

import json
import time
from pathlib import Path
from typing import Literal

from loguru import logger
from pydantic import BaseModel, Field

# -------------- MODEL --------------- #


CONFIG_DIR = Path(__file__).parent
STORE_CONFIG_PATH = CONFIG_DIR / "store.json"


# -------------- MODEL --------------- #


class Store(BaseModel):
    time: int = 0
    time_left: int = 0
    balance: float = 0


# -------------- HELPERS --------------- #


def _load(path: Path, model: type[BaseModel]) -> BaseModel:
    """Load a JSON file into a Pydantic model."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    return model.model_validate_json(path.read_text())


def _save(path: Path, instance: BaseModel) -> None:
    """Persist a Pydantic model back to its JSON file."""
    path.write_text(instance.model_dump_json(indent=2))


# Convenience accessors
def load_risk_config() -> Store:
    return _load(STORE_CONFIG_PATH, Store)


def save_risk_config(sfg: Store) -> None:
    _save(STORE_CONFIG_PATH, sfg)


# ------------ SAVE BALANCE ------------ #


def save_balance():
    return
