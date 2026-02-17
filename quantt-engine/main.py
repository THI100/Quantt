import data.fetch as fetch
import strategy.indicators as indicators
import data.cache as cache
from strategy.signal_generator import get_overall_market_signal

cnd = cache.cached_p42("BTC/USDT")
print(indicators.smr(cnd))