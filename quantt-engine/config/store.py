"""
store.py
Pydantic model for Storing misc variables.
"""

import sys
from datetime import datetime
from pathlib import Path

from loguru import logger
from pydantic import BaseModel

from data.fetch import balance
from persistance.connection import SessionLocal, init_db
from persistance.models import Store

if getattr(sys, "frozen", False):
    DIR = Path(sys.executable).parent
else:
    DIR = Path(__file__).resolve().parent.parent

STORE_CONFIG_PATH = DIR / "qdata" / "store_config.json"
STORE_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

# -------------- MODEL --------------- #


class StorePYD(BaseModel):
    exchange: str = "none"
    last_updated: datetime = datetime.now()
    balances: dict[str, float] = {"USDT": 0.0, "USDC": 0.0}


# -------------- HELPERS --------------- #


class ConfigWatcher:
    """Detects file changes and reloads configuration automatically."""

    def __init__(self, path: Path):
        self.path = path
        self.config = self.reload()
        self.ensure_json_file()

    def ensure_json_file(self):
        init_db()

    def reload(self) -> StorePYD:
        """Force a reload from disk."""
        init_db()
        try:
            return load_store()
        except FileNotFoundError:
            default_sfg = StorePYD()
            save_store(default_sfg)
            return default_sfg

    def get_config(self) -> StorePYD:
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
def load_store() -> StorePYD:
    init_db()
    with SessionLocal() as session:
        row = session.get(Store, "none")
        if row is None:
            if STORE_CONFIG_PATH.exists() and STORE_CONFIG_PATH.stat().st_size:
                legacy = _load(STORE_CONFIG_PATH, StorePYD)
                session.close()
                save_store(legacy)
                return legacy
            raise FileNotFoundError("Store configuration not found in database")
        return StorePYD(
            exchange=row.exchange,
            last_updated=row.data,
            balances={"USDT": row.balance_dt, "USDC": row.balance_dc},
        )


def save_store(sfg: StorePYD) -> None:
    init_db()
    with SessionLocal.begin() as session:
        row = session.get(Store, sfg.exchange) or Store(exchange=sfg.exchange)
        row.data = sfg.last_updated
        row.balance_dt = sfg.balances.get("USDT", 0.0)
        row.balance_dc = sfg.balances.get("USDC", 0.0)
        session.add(row)


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
        initial_store = StorePYD()
        save_store(initial_store)
        return initial_store
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        return None
