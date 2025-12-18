import strategy.indicators as indicators
from data import cache
from config import settings

def get_signal_indicators (market: str):

    market_force_bullish = 0
    market_force_bearish = 0

    candles42 = cache.cached_p42(market=market)

    rsi_values = indicators.rsi(candles=candles42)
    actual_movement = ""

    if rsi_values[0] < 30:
        market_force_bullish += 2  # Buy signal
    elif rsi_values[0] > 70:
        market_force_bearish += 2  # Sell signal
    elif rsi_values[0] < 50:
        market_force_bullish += 1  # Slight buy signal
    elif rsi_values[0] > 50:
        market_force_bearish += 1  # Slight sell signal
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

    return market_force_bullish, market_force_bearish, actual_movement

def get_signal_candlestick_patterns(market: str):
    market_force_bullish = 0.0
    market_force_bearish = 0.0
    bullish_confidence = 0
    bearish_confidence = 0

    candles = cache.cached_p14(market=market)
    patterns = indicators.detect_candlestick_patterns(candles=candles)

    print(patterns)

    for p in patterns:
        mult = p["multiplicator"]
        strength = p["volume_strength"]

        impact = abs(mult) * min(strength, 2.0)

        if mult > 0:
            market_force_bullish += impact
            bullish_confidence += 1
        elif mult < 0:
            market_force_bearish += impact
            bearish_confidence += 1

    return (
        market_force_bullish,
        market_force_bearish,
        bullish_confidence,
        bearish_confidence,
    )


def get_signal_smc(market: str):
    market_force_bullish = 0.0
    market_force_bearish = 0.0
    bullish_confidence = 0
    bearish_confidence = 0

    candles = cache.cached_p14(market=market)
    smc_events = indicators.smc_reader(candles=candles)

    for e in smc_events:
        etype = e["type"]
        mult = e["multiplicator"]
        strength = min(e["volume_strength"], 2.0)

        impact = abs(mult) * strength

        # ---------------- Bullish events ----------------
        if etype in ("bos_bullish", "choch_bullish", "bullish_fvg"):
            bullish_confidence += 1

            if etype == "bos_bullish":
                market_force_bullish += impact * 1.5
            elif etype == "choch_bullish":
                market_force_bullish += impact * 2.0
                market_force_bearish *= 0.5
            elif etype == "bullish_fvg":
                market_force_bullish += impact * 0.7

        # ---------------- Bearish events ----------------
        elif etype in ("bos_bearish", "choch_bearish", "bearish_fvg"):
            bearish_confidence += 1

            if etype == "bos_bearish":
                market_force_bearish += impact * 1.5
            elif etype == "choch_bearish":
                market_force_bearish += impact * 2.0
                market_force_bullish *= 0.5
            elif etype == "bearish_fvg":
                market_force_bearish += impact * 0.7

    return (
        market_force_bullish,
        market_force_bearish,
        bullish_confidence,
        bearish_confidence,
    )


def get_overall_market_signal(market: str):
    mbull2, mbear2, actual_movement = get_signal_indicators(market=market)
    mbull1, mbear1, cbull1, cbear1 = get_signal_candlestick_patterns(market=market)
    mbull3, mbear3, cbull3, cbear3 = get_signal_smc(market=market)

    total_bullish = round(mbull1 + mbull2 + mbull3, 2)
    total_bearish = round(mbear1 + mbear2 + mbear3, 2)

    total_confidence_bullish = cbull1 + cbull3
    total_confidence_bearish = cbear1 + cbear3

    real_strength = round(abs(total_bullish - total_bearish), 2)
    real_confidence = abs(total_confidence_bullish - total_confidence_bearish)

    return real_confidence, real_strength, actual_movement