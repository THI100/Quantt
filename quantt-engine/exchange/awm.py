import os
from dotenv import set_key

def ensure_env_file(filepath=".env"):
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write("")
        return {"status": "created", "message": f"{filepath} initialized."}
    return {"status": "exists", "message": f"{filepath} already exists."}

def write_api_credentials(api_key, api_secret, exchange, filepath=".env"):
    ensure_env_file(filepath)
    # Formats keys like BINANCE_API_KEY or COINBASE_API_SECRET
    prefix = exchange.upper().strip()
    set_key(filepath, f"API_KEY_{prefix}", api_key)
    set_key(filepath, f"API_SECRET_{prefix}", api_secret)
    return {"status": "success", "message": f"Updated credentials for {prefix}"}

def remove_env_file(filepath=".env"):
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "deleted", "message": f"{filepath} removed."}
    return {"status": "error", "message": "File not found."}
