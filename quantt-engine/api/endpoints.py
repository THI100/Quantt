import threading
from typing import Dict

from ccxt.base.types import Int
from fastapi import APIRouter, HTTPException

from config import risk, settings
from core.bot import TradingBot
from execution.position_manager import manage_open_symbols as mos

router = APIRouter()
bot = TradingBot()
bot_thread = None
is_paused = False

# ------------------------------------------------------------------ #
#  Helper                                                              #
# ------------------------------------------------------------------ #


def _require_running():
    """Raise 400 if the bot is not active."""
    if not bot.is_running:
        raise HTTPException(status_code=400, detail="Bot is not running.")


# ------------------------------------------------------------------ #
#  Bot control                                                         #
# ------------------------------------------------------------------ #


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
    if not bot.is_running:
        return {"status": "deactivated"}
    threading.Thread(target=bot.stop, daemon=True).start()
    return {"status": "deactivating"}


@router.post("/bot/restart")
def restart_trigger():
    global bot_thread, is_paused
    if bot.is_running:
        bot.stop()
    is_paused = False
    bot_thread = threading.Thread(target=bot.start, daemon=True)
    bot_thread.start()
    return {"status": "restarting"}


@router.post("/bot/pause")
def pause_trigger():
    global is_paused
    _require_running()
    if is_paused:
        return {"status": "already_paused"}
    is_paused = True
    return {"status": "paused"}


@router.post("/bot/resume")
def resume_trigger():
    global is_paused
    _require_running()
    if not is_paused:
        return {"status": "already_running"}
    is_paused = False
    return {"status": "resumed"}


@router.get("/bot/status")
def get_status():
    if not bot.is_running:
        return {"status": "deactivated"}
    markets = mos()
    return {"status": "paused" if is_paused else "active", "markets": markets}


# ------------------------------------------------------------------ #
#  Positions                                                           #
# ------------------------------------------------------------------ #


@router.get("/positions/{symbol}")
def get_position(symbol: str, id: str):
    """Return details for a single open position."""
    _require_running()
    position = bot.fet_order(symbol, id)
    if not position:
        raise HTTPException(status_code=404, detail=f"No open position for '{symbol}'.")
    return position


@router.delete("/positions/{symbol}")
def close_position(symbol: str, id: str):
    """Force-close a position by symbol, sending a market order."""
    _require_running()
    try:
        bot.close_order(symbol, id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to close position: {str(e)}"
        )
    return {"status": "closed", "symbol": symbol}


# ------------------------------------------------------------------ #
#  Reports (skeletons)                                                 #
# ------------------------------------------------------------------ #


@router.get("/report/trades")
def get_trades():
    """
    Paginated list of closed trades.
    TODO: connect to trade history source (DB, file, exchange API, etc.)
    TODO: add query params — e.g. ?page=1&page_size=50&symbol=BTCUSDT&from=date&to=date
    """
    return {
        # TODO: replace with real trade records
        "trades": [],
        "page": 1,
        "page_size": 50,
        "total": 0,
    }


@router.get("/report/trades/summary")
def get_trades_summary():
    """
    Aggregated performance stats across all closed trades.
    TODO: compute from real trade history.
    """
    return {
        # TODO: derive from actual closed trades
        "total_trades": 0,
        "win_rate": 0.0,  # e.g. 0.62 → 62%
        "total_pnl": 0.0,
        "avg_pnl_per_trade": 0.0,
        "avg_hold_time": None,  # TODO: timedelta or seconds
        "sharpe_ratio": None,  # TODO: requires returns series
        "max_drawdown": None,  # TODO: requires equity curve
    }


# ------------------------------------------------------------------ #
#  Config — trading                                                    #
# ------------------------------------------------------------------ #


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


# ------------------------------------------------------------------ #
#  Config — risk                                                       #
# ------------------------------------------------------------------ #


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


@router.get("/config/risk/limits")
def get_risk_limits():
    """
    Return derived risk limits computed from the live balance.
    Requires an exchange call to fetch current account balance.
    TODO: replace bot.get_balance() with your actual exchange balance method.
    """
    try:
        cfg = risk.load_risk_config()
        balance = bot.get_balance()  # TODO: confirm method name on your TradingBot
        return {
            "balance": balance,
            "max_position_size": balance
            * cfg.max_position_pct,  # TODO: confirm field name
            "max_total_exposure": balance
            * cfg.max_total_exposure_pct,  # TODO: confirm field name
            "max_loss_per_trade": balance
            * cfg.max_loss_pct,  # TODO: confirm field name
            # TODO: add any other derived limits from your RiskConfig fields
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to compute risk limits: {str(e)}"
        )
