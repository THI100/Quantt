import threading

from fastapi import APIRouter

from core.bot import TradingBot

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

    return {"status": "started"}


@router.get("/bot/status")
def get_status():
    # This returns immediately, so it doesn't block anything
    return {"is_running": bot.is_running}
