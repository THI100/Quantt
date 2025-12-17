import data.fetch as fetch
import strategy.indicators as indicators
from strategy.signal_generator import get_signal_indicators, get_signal_candlestick_patterns

mb1, mbear1 = get_signal_candlestick_patterns()
mb2, mbear2, movement, rsi_cv = get_signal_indicators()
total_bullish = round(mb1 + mb2, 2)
total_bearish = round(mbear1 + mbear2, 2)

print(f"Total Bullish Force: {total_bullish}")
print(f"Total Bearish Force: {total_bearish}")
print(f"Actual Market Movement: {movement}")
print(f"Current RSI Value: {rsi_cv}")