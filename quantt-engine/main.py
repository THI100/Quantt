import uvicorn
from fastapi import FastAPI

import core.bot as bot
from api import principal, report, set
from utils import log

app = FastAPI(title="quantt_engine")

# Create instances of logging and TradingBot.
log.setup_logging()
my_bot = bot.TradingBot()
app.include_router(principal.route)
app.include_router(report.r_route)
app.include_router(set.s_route)

if __name__ == "__main__":
    # Run the web server
    uvicorn.run(app, host="0.0.0.0", port=8000)
