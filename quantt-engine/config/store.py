"""
store.py
Pydantic model for Storing misc variables.
"""

import os
from datetime import datetime
from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from data.fetch import balance

# -------------- PATHS --------------- #


DIR = Path(__file__).parent
STORE_CONFIG_PATH = DIR.parent / "qdata" / "store_config.json"
STORE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

# -------------- MODEL --------------- #


class Store(BaseModel):
    last_updated: datetime = datetime.now()
    balances: dict[str, float] = {"USDT": 0.0, "USDC": 0.0}


# -------------- HELPERS --------------- #


class ConfigWatcher:
    """Detects file changes and reloads configuration automatically."""

    def __init__(self, path: Path):
        self.path = path
        self._last_mtime = 0
        self.config = self.reload()
        self.ensure_json_file()

    def ensure_json_file(self, fpath=STORE_CONFIG_PATH):
        fpath.parent.mkdir(parents=True, exist_ok=True)
        if not os.path.exists(fpath):
            with open(fpath, "w") as f:
                f.write("")
            return logger.info(f"Created file: {fpath}")

    def reload(self) -> Store:
        """Force a reload from disk."""
        if not self.path.exists():
            # If file doesn't exist, save defaults to create it
            default_sfg = Store()
            save_store(default_sfg)
            return default_sfg

        self._last_mtime = self.path.stat().st_mtime
        return load_store()

    def get_config(self) -> Store:
        current_mtime = self.path.stat().st_mtime
        if current_mtime > self._last_mtime:
            self.config = self.reload()

        return self.config


def _load(path: Path, model: type[BaseModel]) -> BaseModel:
    """Load a JSON file into a Pydantic model."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    return model.model_validate_json(path.read_text())


def _save(path: Path, instance: BaseModel) -> None:
    """Persist a Pydantic model back to its JSON file."""
    path.write_text(instance.model_dump_json(indent=2))


# Convenience accessors
def load_store() -> Store:
    return _load(STORE_CONFIG_PATH, Store)


def save_store(sfg: Store) -> None:
    _save(STORE_CONFIG_PATH, sfg)


watcher = ConfigWatcher(STORE_CONFIG_PATH)


# ------------ SAVE BALANCE ------------ #


def initialize():
    """
    Checks the store.
    - If a balance already exists: Returns current data (No Write).
    - If no balance is set: Fetches balances and saves (Write).
    """
    try:
        # 1. Load the existing config
        current_store = load_store()

        # 2. THE LOCK: If a non-zero balance already exists, do nothing
        has_balance = any(v > 0.0 for v in current_store.balances.values())
        if has_balance:
            logger.info("Store already has a balance. Skipping update.")
            return current_store

        # 3. NO BALANCE: Fetch and save once
        logger.info("No balance found. Fetching and saving initial balance...")

        bal = balance()
        usdt_total = bal.get("USDT", {}).get("total", 0.0)
        usdc_total = bal.get("USDC", {}).get("total", 0.0)

        current_store.balances = {"USDT": usdt_total, "USDC": usdc_total}
        current_store.last_updated = datetime.now()

        save_store(current_store)
        return current_store

    except FileNotFoundError:
        logger.warning("No store.json found. Creating initial file.")
        initial_store = Store()
        save_store(initial_store)
        return initial_store
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return None
