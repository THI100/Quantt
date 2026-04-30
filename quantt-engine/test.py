from utils import log
from core import bot

log.setup_logging()
my_bot = bot.TradingBot()

my_bot.setup_environment()
my_bot.start()
