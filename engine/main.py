import data.fetch as fetch
import strategy.indicators as indicators
from strategy.signal_generator import get_signal_indicators

print (get_signal_indicators())

# print (fetch.get_OHLCV("SOL/USDT", "1h", 5))