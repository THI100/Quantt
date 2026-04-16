import threading

from fastapi import APIRouter, HTTPException

from core.bot import TradingBot
from execution.position_manager import manage_open_symbols as mos

route = APIRouter()
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

@route.post("/bot/start")
def start_trigger():
    global bot_thread
    if bot.is_running:
        return {"status": "already_running"}
    bot_thread = threading.Thread(target=bot.start, daemon=True)
    bot_thread.start()
    return {"status": "activating"}


@route.post("/bot/stop")
def stop_trigger():
    if not bot.is_running:
        return {"status": "deactivated"}
    threading.Thread(target=bot.stop, daemon=True).start()
    return {"status": "deactivating"}


@route.post("/bot/restart")
def restart_trigger():
    global bot_thread, is_paused
    if bot.is_running:
        bot.stop()
    is_paused = False
    bot_thread = threading.Thread(target=bot.start, daemon=True)
    bot_thread.start()
    return {"status": "restarting"}


@route.post("/bot/pause")
def pause_trigger():
    global is_paused
    _require_running()
    if is_paused:
        return {"status": "already_paused"}
    is_paused = True
    return {"status": "paused"}


@route.post("/bot/resume")
def resume_trigger():
    global is_paused
    _require_running()
    if not is_paused:
        return {"status": "already_running"}
    is_paused = False
    return {"status": "resumed"}


@route.get("/bot/status")
def get_status():
    if not bot.is_running:
        return {"status": "deactivated"}
    markets = mos()
    return {"status": "paused" if is_paused else "active", "markets": markets}
