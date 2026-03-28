import uvicorn
from fastapi import FastAPI

import core.bot as bot
from api.endpoints import router
from utils import log

# app = FastAPI(title="quantt_engine")

# Create instances of logging and TradingBot.
log.setup_logging()
my_bot = bot.TradingBot()
# app.include_router(router)

print(my_bot.check_bal())
my_bot.start()

# if __name__ == "__main__":
#     # Run the web server
#     uvicorn.run(app, host="0.0.0.0", port=8000)
