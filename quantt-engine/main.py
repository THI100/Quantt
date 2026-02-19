import data.cache as cache
import data.fetch as fetch
import strategy.indicators as indicators
from strategy.signal_generator import get_overall_market_signal

cnd = cache.cached_p14("BTC/USDT")
print(indicators.smr(cnd))
print(cnd)
