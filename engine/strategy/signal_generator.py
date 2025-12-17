import strategy.indicators as indicators
from data import cache, fetch
from execution.order_manager import market
from config import settings

def get_signal_indicators ():

    market_force_bullish = 0
    market_force_bearish = 0

    candles14 = cache.cached_p14(market=market)
    candles42 = cache.cached_p42(market=market)

    rsi_values = indicators.rsi(candles=candles42)
    actual_movement = ""

    if rsi_values[0] < 30:
        market_force_bullish += 1  # Buy signal
    elif rsi_values[0] > 70:
        market_force_bearish += 1  # Sell signal
    else:
        market_force_bullish += 0  # Neutral signal

    rsi_gap_mult = rsi_values[0] / rsi_values[1]

    if rsi_gap_mult < 1:
        rsi_gap_mult_impact = abs((rsi_gap_mult - 1) * 10)
        market_force_bearish += rsi_gap_mult_impact  # Sell signal
    elif rsi_gap_mult > 1:
        rsi_gap_mult_impact = abs((rsi_gap_mult - 1) * 10)
        market_force_bullish += rsi_gap_mult_impact  # Buy signal
    else:
        market_force_bullish += 0  # Neutral signal

    tenkan, kijun = indicators.tenkan_and_kijun(candles=candles42)

    atr_value = indicators.atr(candles42, period=14)
    atr_multiplier = settings.atr_multiplier
    buffer = atr_multiplier * atr_value

    diff = tenkan - kijun

    if diff > buffer:
        market_force_bullish += 1
        actual_movement = "bullish"

    elif diff < -buffer:
        market_force_bearish += 1
        actual_movement = "bearish"

    else:
        actual_movement = "neutral"


    return market_force_bullish, market_force_bearish, actual_movement, rsi_values[0]

def get_signal_candlestick_patterns(
    market: str = market,
):
    market_force_bullish = 0.0
    market_force_bearish = 0.0

    # shared cached snapshot
    candles = cache.cached_p14(market=market)

    patterns = indicators.detect_candlestick_patterns(candles=candles)

    for p in patterns:
        mult = p["multiplicator"]
        strength = p["volume_strength"]

        # normalize multiplicator impact
        impact = abs(mult) * min(strength, 2.0)

        if mult > 0:
            market_force_bullish += impact
        elif mult < 0:
            market_force_bearish += impact

    return market_force_bullish, market_force_bearish