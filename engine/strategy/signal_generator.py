import strategy.indicators as indicators
from data import cache
from config import settings
from utils.math import scale_0_100

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

    candles = cache.cached_p28(market=market)
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
    """
    This function returns a general market signal based on multiple strategies.
    It combines signals from indicators, candlestick patterns, and SMC analysis
    to determine the overall market sentiment.
     - Returns:
        - real_confidence (float): Confidence level of the signal (0-100).
        - real_strength (float): Strength of the signal (0-100).
        - actual_movement (str): Actual market movement ("bullish", "bearish", "neutral").
        - direction (str): Overall market direction ("bullish", "bearish", "neutral").
    """
    mbull2, mbear2, actual_movement = get_signal_indicators(market)
    mbull1, mbear1, cbull1, cbear1 = get_signal_candlestick_patterns(market)
    mbull3, mbear3, cbull3, cbear3 = get_signal_smc(market)

    bullish = mbull1 + mbull2 + mbull3
    bearish = mbear1 + mbear2 + mbear3

    conf_bull = cbull1 + cbull3
    conf_bear = cbear1 + cbear3

    real_strength_raw = bullish - bearish

    direction = (
        "bullish" if real_strength_raw > 0
        else "bearish" if real_strength_raw < 0
        else "neutral"
    )

    real_confidence_raw = (
        conf_bull if real_strength_raw > 0
        else conf_bear if real_strength_raw < 0
        else 0
    )

    max_strength = bullish + bearish
    max_confidence = conf_bull + conf_bear

    real_strength = scale_0_100(real_strength_raw, max_strength)
    real_confidence = scale_0_100(real_confidence_raw, max_confidence)

    if real_confidence == 0:
        direction = "neutral"

    return real_confidence, real_strength, actual_movement, direction

def get_loss_and_profit_stops(market: str, real_confidence: float, real_strength: float, actual_movement: str, direction: str):
    """
    This function serves to get the stop_loss and take_profit of a determinited market.
    Based on the strength and confidence of the market movement.
    Determining the market based on previous smc movements and market structures/paterns.
    """

    candles = cache.cached_p14(market)

    return 