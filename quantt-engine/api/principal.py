import threading

from fastapi import APIRouter, HTTPException

from core.bot import TradingBot
from execution.position_manager import manage_open_symbols as mos

route = APIRouter()
bot = TradingBot()
bot_thread = None

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

@route.post("/")
def setup():
    try:
        bot.setup_environment()
        return {"status": "success", "message": "Environment set successfully"}
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        return {"status": "error", "message": str(e)}, 500

@route.post("/bot/start")
def start_trigger():
    if bot.is_running:
        return {"status": "Online"}

    bot_thread = threading.Thread(target=bot.start, daemon=True)
    bot_thread.start()
    return {"status": "Online"}


@route.post("/bot/stop")
def stop_trigger():
    if not bot.is_running:
        return {"status": "Already Offline"}
    bot.stop()
    return {"status": "Offline"}


@route.post("/bot/restart")
def restart_trigger():
    bot.stop()
    # Give the thread a tiny window to exit the while loop
    time.sleep(1)
    return start_trigger()


@route.get("/bot/status")
def get_status():
    if not bot.is_running:
        return {"status": "Offline"}
    return {"status": "Online"}
