import threading

from fastapi import APIRouter

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
    bot_thread.stop()

    return {"status": "deactivating"}


@router.get("/bot/status")
def get_status():
    global bot_thread
    if bot.is_running == False:
        return {"status": "deactivated"}

    bot_thread = threading.Thread(target=mos, deamon=True)
    markets = bot_thread.mos()
    # This returns the open markets and etc, it is a dict, equivalent of a object for JS.
    return markets, {"status": "active"}
