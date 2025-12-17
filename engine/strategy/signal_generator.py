import strategy.indicators as indicators
from data import cache, fetch
from execution.order_manager import market # type: ignore

def get_signal_indicators ():

    market_force_bullish = 0
    market_force_bearish = 0


    candles = cache.cached_p42(market=market)

    rsi_values = indicators.rsi(candles=candles)

    if rsi_values[0] < 30:
        market_force_bullish += 1  # Buy signal
    elif rsi_values[0] > 70:
        market_force_bearish += 1  # Sell signal
    else:
        market_force_bullish += 0  # Neutral signal

    print(rsi_values[0], rsi_values[1])

    rsi_gap_mult = rsi_values[0] / rsi_values[1]

    if rsi_gap_mult < 1:
        rsi_gap_mult_impact = abs((rsi_gap_mult - 1) * 10)
        market_force_bearish += rsi_gap_mult_impact  # Sell signal
    elif rsi_gap_mult > 1:
        rsi_gap_mult_impact = abs((rsi_gap_mult - 1) * 10)
        market_force_bullish += rsi_gap_mult_impact  # Buy signal
    else:
        market_force_bullish += 0  # Neutral signal

    tenkan, kijun = indicators.tenkan_and_kijun(candles=candles)
    if tenkan > kijun:
        market_force_bullish += 1  # Buy signal
    elif tenkan < kijun:
        market_force_bearish += 1  # Sell signal
    else:
        market_force_bullish += 0  # Neutral signal

    return market_force_bullish, market_force_bearish
