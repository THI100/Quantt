import data.fetch as fetch
import strategy.indicators as indicators
import data.cache as cache
from strategy.signal_generator import get_overall_market_signal

print(get_overall_market_signal("ZEC/USDT"))