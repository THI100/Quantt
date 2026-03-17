import asyncio

import strategy.indicators as indicators
from config import risk, settings
from data import cache
from utils.math import scale_0_100


async def get_signal_indicators(candles42: list):
    market_force_bullish = 0
    market_force_bearish = 0

    # ================= RSI =================
    rsi_values = indicators.rsi(candles=candles42)

    if rsi_values[0] < 30:
        market_force_bullish += 2
    elif rsi_values[0] > 70:
        market_force_bearish += 2
    elif rsi_values[0] < 50:
        market_force_bullish += 1
    elif rsi_values[0] > 50:
        market_force_bearish += 1

    rsi_gap_mult = rsi_values[0] / rsi_values[1]
    gap_impact = abs((rsi_gap_mult - 1) * 10)
    if rsi_gap_mult < 1:
        market_force_bearish += gap_impact
    else:
        market_force_bullish += gap_impact

    # ================= TENKAN / KIJUN =================
    tenkan, kijun = indicators.tenkan_and_kijun(candles=candles42)
    atr_value = indicators.atr(candles42, period=14)
    buffer = risk.atr_multiplier * atr_value
    diff = tenkan - kijun

    if diff > buffer:
        actual_movement = "bullish"
        market_force_bullish += 1
    elif diff < -buffer:
        actual_movement = "bearish"
        market_force_bearish += 1
    else:
        actual_movement = "neutral"

    # ================= MACD =================
    macd_val, signal_val, hist_val, *_ = indicators.macd(candles=candles42)

    if macd_val > signal_val:
        market_force_bullish += 1
    else:
        market_force_bearish += 1

    if macd_val > 0:
        market_force_bullish += 0.5
    else:
        market_force_bearish += 0.5

    hist_weight = min(abs(hist_val) / 50, 2)
    if hist_val > 0:
        market_force_bullish += hist_weight
    else:
        market_force_bearish += hist_weight

    return market_force_bullish, market_force_bearish, actual_movement


async def get_signal_candlestick_patterns(candles14: list):
    bull_f, bear_f, bull_c, bear_c = 0.0, 0.0, 0, 0
    patterns = indicators.detect_candlestick_patterns(candles=candles14)

    for p in patterns:
        impact = abs(p["multiplicator"]) * min(p["volume_strength"], 2.0)
        if p["multiplicator"] > 0:
            bull_f += impact
            bull_c += 1
        else:
            bear_f += impact
            bear_c += 1
    return bull_f, bear_f, bull_c, bear_c


async def get_signal_smr(candles28: list):
    bull_f, bear_f, bull_c, bear_c = 0.0, 0.0, 0, 0
    smr_events = indicators.smr(candles=candles28)

    for e in smr_events:
        etype, impact = (
            e["type"],
            abs(e["multiplicator"]) * min(e["volume_strength"], 2.0),
        )

        if "bullish" in etype:
            bull_c += 1
            if etype == "bos_bullish":
                bull_f += impact * 1.5
            elif etype == "choch_bullish":
                bull_f += impact * 2.0
                bear_f *= 0.5
            elif etype == "bullish_fvg":
                bull_f += impact * 0.7

        elif "bearish" in etype:
            bear_c += 1
            if etype == "bos_bearish":
                bear_f += impact * 1.5
            elif etype == "choch_bearish":
                bear_f += impact * 2.0
                bull_f *= 0.5
            elif etype == "bearish_fvg":
                bear_f += impact * 0.7

    return bull_f, bear_f, bull_c, bear_c


async def get_overall_market_signal(market: str):
    # OPTIMIZATION: Fetch all cache data in parallel first
    c14_task = cache.cached_p14(market=market)
    c28_task = cache.cached_p28(market=market)
    c42_task = cache.cached_p42(market=market)

    candles14, candles28, candles42 = await asyncio.gather(c14_task, c28_task, c42_task)

    # Execute signal logic in parallel
    results = await asyncio.gather(
        get_signal_indicators(market, candles42),
        get_signal_candlestick_patterns(market, candles14),
        get_signal_smr(market, candles28),
    )

    (
        (mbull2, mbear2, actual_movement),
        (mbull1, mbear1, cbull1, cbear1),
        (mbull3, mbear3, cbull3, cbear3),
    ) = results

    bullish = mbull1 + mbull2 + mbull3
    bearish = mbear1 + mbear2 + mbear3
    real_strength_raw = bullish - bearish

    direction = "neutral"
    if real_strength_raw > 0:
        direction = "bullish"
    elif real_strength_raw < 0:
        direction = "bearish"

    real_conf_raw = (
        (cbull1 + cbull3)
        if direction == "bullish"
        else (cbear1 + cbear3)
        if direction == "bearish"
        else 0
    )

    max_strength = bullish + bearish
    max_confidence = (cbull1 + cbull3) + (cbear1 + cbear3)

    real_strength = (
        scale_0_100(real_strength_raw, max_strength) if max_strength > 1 else 0
    )
    real_confidence = (
        scale_0_100(real_conf_raw, max_confidence) if max_confidence > 1 else 0
    )

    if real_confidence == 0:
        direction = "neutral"

    return real_confidence, real_strength, actual_movement, direction


async def get_loss_and_profit_stops(market: str, direction: str):
    candles = await cache.cached_p42(market)
    actual_value = candles[-1][4]
    stop_losses_events = indicators.smr(candles=candles)

    last_high_val, last_low_val = None, None

    for a in stop_losses_events:
        idx = max(0, a["index"] - 2)
        if a["type"] in ("HH", "LH"):
            last_high_val = candles[idx][2]
        elif a["type"] in ("HL", "LL"):
            last_low_val = candles[idx][3]

    if direction == "bullish":
        stop_loss = min(
            last_low_val if last_low_val else actual_value * 0.98, actual_value * 0.99
        )
        take_profit = actual_value + (
            (actual_value - stop_loss) * risk.risk_reward_ratio
        )
    else:
        stop_loss = max(
            last_high_val if last_high_val else actual_value * 1.02, actual_value * 1.01
        )
        take_profit = actual_value - (
            (stop_loss - actual_value) * risk.risk_reward_ratio
        )

    return stop_loss, take_profit, actual_value
