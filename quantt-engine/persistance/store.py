"""
store.py
Pydantic model for Storing misc variables.
"""

import os
from datetime import datetime, time, timedelta
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, computed_field

from data.fetch import balance

# -------------- MODEL --------------- #


CONFIG_DIR = Path(__file__).parent
STORE_CONFIG_PATH = CONFIG_DIR / "store_config.json"
SECONDS_IN_A_DAY = 86400


# -------------- MODEL --------------- #


class Store(BaseModel):
    last_updated: datetime = datetime.now()
    balances: dict[str, float] = {"USDT": 0.0, "USDC": 0.0}

    @computed_field
    @property
    def time_left(self) -> int:
        """Returns seconds remaining until the end of the current day."""
        now = datetime.now()
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time.min)
        return int((tomorrow - now).total_seconds())


# -------------- HELPERS --------------- #


class ConfigWatcher:
    """Detects file changes and reloads configuration automatically."""

    def __init__(self, path: Path):
        self.path = path
        self._last_mtime = 0
        self.config = self.reload()
        self.ensure_json_file()

    def ensure_json_file(self, fpath=STORE_CONFIG_PATH):
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

        # Check for day rollover
        if self.config.last_updated.date() < datetime.now().date():
            logger.info("New day detected! Resetting store totals.")
            self.config = Store()  # Reset to defaults
            save_store(self.config)

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
    - If today matches the file: Returns current data (No Write).
    - If it's a new day: Fetches balances, resets, and saves (Write).
    """
    try:
        # 1. Load the existing config to check the date
        current_store = load_store()

        today = datetime.now().date()
        last_recorded_day = current_store.last_updated.date()

        # 2. THE LOCK: Check if we are still on the same day
        if last_recorded_day == today:
            logger.info("Store already initialized for today. Skipping update.")
            return current_store

        # 3. NEW DAY LOGIC: Only runs if the 'if' above is false
        logger.info("New day detected! Updating store.json...")

        bal = balance()
        usdt_total = bal.get("USDT", {}).get("total", 0.0)
        usdc_total = bal.get("USDC", {}).get("total", 0.0)

        # Update the instance
        current_store.balances = {"USDT": usdt_total, "USDC": usdc_total}
        current_store.last_updated = datetime.now()

        # 4. Save to disk (Only happens once per day)
        save_store(current_store)
        return current_store

    except FileNotFoundError:
        logger.warning("No store.json found. Creating initial file.")
        initial_store = Store()  # This will use defaults
        save_store(initial_store)
        return initial_store
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return None
