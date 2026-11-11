import threading
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from loguru import logger

from config import store
from core.bot import TradingBot
from exchange.awm import ensure_env_file
from utils.stream_manager import log_stream

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
        _ = store.initialize()
        _ = ensure_env_file()
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
    time.sleep(1)
    return start_trigger()


@route.get("/bot/status")
def get_status():
    if not bot.is_running:
        return {"status": "Offline"}
    return {"status": "Online"}


@route.get("/test")
def test_server():
    """Report that the API process is healthy and able to serve requests."""
    try:
        return {"status": "running", "message": "Server is running."}
    except Exception as e:
        logger.exception("Health check failed")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": f"Server error: {e}"},
        )


@route.get("/bot/logging")
def log_sink():
    return StreamingResponse(log_stream.generator(), media_type="text/event-stream")
