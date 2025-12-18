import strategy.indicators as indicators
from data import cache
from config import settings

def get_signal_indicators (market: str):

    market_force_bullish = 0
    market_force_bearish = 0
    confidence = 0

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
        confidence = abs(diff) / buffer

    elif diff < -buffer:
        market_force_bearish += 1
        actual_movement = "bearish"
        confidence = abs(diff) / buffer

    else:
        actual_movement = "neutral"
        confidence = 0


    return market_force_bullish, market_force_bearish, actual_movement, confidence

def get_signal_candlestick_patterns(market: str):
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

def get_signal_smc(market: str):
    market_force_bullish = 0.0
    market_force_bearish = 0.0

    candles = cache.cached_p14(market=market)

    smc_events = indicators.smc_reader(
        candles=candles,
    )

    for e in smc_events:
        etype = e["type"]
        mult = abs(e["multiplicator"])
        strength = min(e["volume_strength"], 2.0)

        impact = mult * strength

        # ---------------- Bullish events ----------------
        if etype == "bos_bullish":
            market_force_bullish += impact * 1.5

        elif etype == "choch_bullish":
            market_force_bullish += impact * 2.0
            market_force_bearish *= 0.5

        elif etype == "bullish_fvg":
            market_force_bullish += impact * 0.7

        # ---------------- Bearish events ----------------
        elif etype == "bos_bearish":
            market_force_bearish += impact * 1.5

        elif etype == "choch_bearish":
            market_force_bearish += impact * 2.0
            market_force_bullish *= 0.5

        elif etype == "bearish_fvg":
            market_force_bearish += impact * 0.7

    return market_force_bullish, market_force_bearish

def get_overall_market_signal(market: str):
    mb1, mbear1 = get_signal_candlestick_patterns(market=market)
    mb2, mbear2, movement, confidence = get_signal_indicators(market=market)
    mb3, mbear3 = get_signal_smc(market=market)

    total_bullish = round(mb1 + mb2 + mb3, 2)
    total_bearish = round(mbear1 + mbear2 + mbear3, 2)

    print(f"[{market}] Market Signal - Bullish: {total_bullish} | Bearish: {total_bearish} | Movement: {movement} | Confidence: {confidence:.2f}")
    
    original_market_balance = total_bullish / total_bearish

    if movement == "bullish":
        new_bullish = total_bullish * confidence
        total_bullish = round(new_bullish, 2)
    elif movement == "bearish":
        new_bearish = total_bearish * confidence
        total_bearish = round(new_bearish, 2)
    else:
        pass

    strength = abs(total_bullish / total_bearish)
    if strength < 1.0:
        movement = "neutral"
    

    return total_bullish, total_bearish, movement, original_market_balance