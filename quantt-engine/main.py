import core.bot as bot
from utils import log

# Create instances of logging and TradingBot.
log.setup_logging()
my_bot = bot.TradingBot()

my_bot.start()
