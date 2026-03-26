import threading
from typing import Dict

from fastapi import APIRouter, HTTPException

from config import risk, settings
from core.bot import TradingBot
from execution.position_manager import manage_open_symbols as mos

router = APIRouter()
bot = TradingBot()
bot_thread = None


# sync, so do not change it to async, due to the whole bot architecture.
@router.post("/bot/start")
def start_trigger():
    global bot_thread
    if bot.is_running:
        return {"status": "already_running"}

    bot_thread = threading.Thread(target=bot.start, daemon=True)
    bot_thread.start()

    return {"status": "activating"}


@router.post("/bot/stop")
def stop_trigger():
    global bot_thread
    if bot.is_running == False:
        return {"status": "deactivated"}

    bot_thread = threading.Thread(target=bot.stop, daemon=True)
    bot_thread.start()

    return {"status": "deactivating"}


@router.get("/bot/status")
def get_status():
    if not bot.is_running:
        return {"status": "deactivated"}
    markets = mos()  # call directly, not via Thread
    return {"status": "active", "markets": markets}


# --- Setup for config/settings --- #


@router.get("/config/trading", response_model=settings.TradingConfig)
def get_trading_config():
    """Return the current trading configuration."""
    try:
        return settings.load_trading_config()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/config/trading", response_model=settings.TradingConfig)
def update_trading_config(new_cfg: settings.TradingConfig):
    """Overwrite the entire trading configuration."""
    settings.save_trading_config(new_cfg)
    return new_cfg


@router.patch("/config/trading", response_model=settings.TradingConfig)
def patch_trading_config(partial: dict):
    """Partially update the trading configuration (only provided fields change)."""
    current = settings.load_trading_config()
    updated = current.model_copy(update=partial)
    settings.save_trading_config(updated)
    return updated


# --- Risk config --- #


@router.get("/config/risk", response_model=risk.RiskConfig)
def get_risk_config():
    """Return the current risk configuration."""
    try:
        return risk.load_risk_config()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/config/risk", response_model=risk.RiskConfig)
def update_risk_config(new_cfg: risk.RiskConfig):
    """Overwrite the entire risk configuration."""
    risk.save_risk_config(new_cfg)
    return new_cfg


@router.patch("/config/risk", response_model=risk.RiskConfig)
def patch_risk_config(partial: dict):
    """Partially update the risk configuration (only provided fields change)."""
    current = risk.load_risk_config()
    updated = current.model_copy(update=partial)
    risk.save_risk_config(updated)
    return updated
