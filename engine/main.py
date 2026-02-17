import data.fetch as fetch
import strategy.indicators as indicators
import data.cache as cache
from strategy.signal_generator import get_overall_market_signal

tick = fetch.get_ticker("BTC/USDT")
last_price = tick['last']

print(last_price)

print(tick)