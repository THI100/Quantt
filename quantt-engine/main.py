# import data.cache as cache
# import data.fetch as fetch
# import strategy.indicators as indicators
from strategy.signal_generator import get_overall_market_signal

print(get_overall_market_signal("BTC/USDT"))
