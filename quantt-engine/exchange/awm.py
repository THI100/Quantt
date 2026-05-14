import os
import sys
from pathlib import Path

from dotenv import set_key

if getattr(sys, "frozen", False):
    DIR = Path(sys.executable).parent
else:
    DIR = Path(__file__).resolve().parent.parent

ENV_PATH = DIR / "qdata" / ".env"
ENV_PATH.parent.mkdir(parents=True, exist_ok=True)


def ensure_env_file(filepath=ENV_PATH):
    filepath.parent.mkdir(parents=True, exist_ok=True)

    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write("")
        return {"status": "created", "message": f"{filepath} initialized."}
    return {"status": "exists", "message": f"{filepath} already exists."}


def write_api_credentials(api_key, api_secret, exchange, filepath=ENV_PATH):
    ensure_env_file(filepath)
    # Formats keys like BINANCE_API_KEY or COINBASE_API_SECRET
    prefix = exchange.upper().strip()
    set_key(filepath, f"API_KEY_{prefix}", api_key, quote_mode="never")
    set_key(filepath, f"API_SECRET_{prefix}", api_secret, quote_mode="never")
    return {"status": "success", "message": f"Updated credentials for {prefix}"}


def remove_env_file(filepath=ENV_PATH):
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "deleted", "message": f"{filepath} removed."}
    return {"status": "error", "message": "File not found."}
