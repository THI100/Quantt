import numpy as np
import data.cache as cache
from typing import Dict, List
import utils.math as smath

#----------------------------------------------------------------------#

#---------------- TECHNICAL INDICATORS ----------------#

#----------RSI-indicator----------#

def rsi(
    candles=cache.cached_p42(),
    period: int = 14,
    mode: str = "close-close",  # "close-close" (standard) | "open-close"
):
    """
    Returns:
        rsi_value: float   # last RSI value
        rsi_mean:  float   # mean RSI over the window
    """

    if len(candles) < period + 1:
        raise ValueError("Not enough candles to compute RSI")

    candles = np.asarray(candles, dtype=float)

    opens = candles[:, 1]
    closes = candles[:, 4]

    # --- price deltas ---
    if mode == "close-close":
        deltas = np.diff(closes)
    elif mode == "open-close":
        deltas = closes - opens
    else:
        raise ValueError("mode must be 'close-close' or 'open-close'")

    # --- gains / losses ---
    gains = np.clip(deltas, 0.0, None)
    losses = np.clip(-deltas, 0.0, None)

    # --- Wilder initialization (first 14) ---
    avg_gain = gains[:period].mean()
    avg_loss = losses[:period].mean()

    rsi_series = []

    # --- Wilder smoothing over remaining candles ---
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

        if avg_loss == 0:
            rsi_val = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi_val = 100.0 - (100.0 / (1.0 + rs))

        rsi_series.append(rsi_val)

    rsi_value = rsi_series[-1]
    rsi_mean = float(np.mean(rsi_series))

    return rsi_value, rsi_mean, rsi_series

#----------TnK-indicator----------#

def tenkan_and_kijun(
    candles=cache.cached_p42(),
    conversion_period: int = 9,   # Tenkan-sen
    base_period: int = 26,        # Kijun-sen
):
    """
    Returns:
        tenkan_sen: float  # Conversion Line (9)
        kijun_sen:  float  # Base Line (26)
    """

    if len(candles) < base_period:
        raise ValueError("Not enough candles for Ichimoku")

    candles = np.asarray(candles, dtype=float)

    highs = candles[:, 2]
    lows = candles[:, 3]

    # --- Conversion Line (Tenkan-sen) ---
    tenkan_high = np.max(highs[-conversion_period:])
    tenkan_low  = np.min(lows[-conversion_period:])
    tenkan_sen  = (tenkan_high + tenkan_low) / 2.0

    # --- Base Line (Kijun-sen) ---
    kijun_high = np.max(highs[-base_period:])
    kijun_low  = np.min(lows[-base_period:])
    kijun_sen  = (kijun_high + kijun_low) / 2.0

    return tenkan_sen, kijun_sen

#----------------------------------------------------------------------#

# ============================================================
# Candlestick Pattern Reader (STRICT VERSION)
# ============================================================

def detect_candlestick_patterns(
    candles=cache.cached_p42(),
    volume_period: int = 20,
    min_volume_strength: float = 1.24,
) -> List[Dict]:

    candles = np.asarray(candles, dtype=float)
    avg_vol = smath.average_volume(candles, volume_period)

    patterns = []

    for i in range(1, len(candles)):
        prev = candles[i - 1]
        curr = candles[i]

        body_p, _, _ = smath.candle_parts(prev)
        body_c, uw, lw = smath.candle_parts(curr)

        if body_p == 0:
            continue  # avoid doji-engulfed noise

        volume_strength = curr[5] / avg_vol if avg_vol > 0 else 0.0
        if volume_strength < min_volume_strength:
            continue

        # ----------------------------------------------------
        # Engulfing (strict, body-based)
        # ----------------------------------------------------
        multiplier = body_c / body_p

        if multiplier >= 2:
            if curr[4] > curr[1] and prev[4] < prev[1]:
                patterns.append({
                    "type": "bullish_engulfing",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(multiplier),
                    "volume_strength": volume_strength,
                })
                continue

            if curr[4] < curr[1] and prev[4] > prev[1]:
                patterns.append({
                    "type": "bearish_engulfing",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(-multiplier),
                    "volume_strength": volume_strength,
                })
                continue

        # ----------------------------------------------------
        # Hammer / Shooting Star / Hanging Man / Inverted Hammer
        # ----------------------------------------------------
        if body_c > 0:
            # Hammer / Hanging Man (long lower wick)
            if lw >= 2 * body_c and uw <= body_c:
                mult = lw / body_c
                patterns.append({
                    "type": "hammer_like",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(mult),
                    "volume_strength": volume_strength,
                })
                continue

            # Shooting Star / Inverted Hammer (long upper wick)
            if uw >= 2 * body_c and lw <= body_c:
                mult = uw / body_c
                patterns.append({
                    "type": "shooting_star_like",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(-mult),
                    "volume_strength": volume_strength,
                })
                continue

        # ----------------------------------------------------
        # Dragonfly / Gravestone Doji (wick dominance)
        # ----------------------------------------------------
        if body_c > 0:
            if lw >= 3 * body_c and uw <= body_c * 0.2:
                mult = lw / body_c
                patterns.append({
                    "type": "dragonfly_doji",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(mult),
                    "volume_strength": volume_strength,
                })
                continue

            if uw >= 3 * body_c and lw <= body_c * 0.2:
                mult = uw / body_c
                patterns.append({
                    "type": "gravestone_doji",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(-mult),
                    "volume_strength": volume_strength,
                })
                continue

        # ----------------------------------------------------
        # Doji Star (relative to previous body)
        # ----------------------------------------------------
        if body_c < body_p * 0.3 and (uw + lw) > body_p:
            mult = (uw + lw) / body_p
            sign = 1 if curr[4] > curr[1] else -1
            patterns.append({
                "type": "doji_star",
                "index": i,
                "multiplicator": smath.clamp_multiplier(sign * mult),
                "volume_strength": volume_strength,
            })

    return patterns


# ============================================================
# Smart Money Concept Reader (STRICT VERSION)
# ============================================================

def smc_reader(
    candles=cache.cached_p42(),
    swing_left: int = 2,
    swing_right: int = 2,
    volume_period: int = 20,
    min_volume_strength: float = 1.24,
) -> List[Dict]:

    candles = np.asarray(candles, dtype=float)
    avg_vol = smath.average_volume(candles, volume_period)

    events = []

    highs = candles[:, 2]
    lows = candles[:, 3]

    swing_highs = []
    swing_lows = []

    for i in range(swing_left, len(candles) - swing_right):
        if highs[i] == np.max(highs[i - swing_left:i + swing_right + 1]):
            swing_highs.append((i, highs[i]))
        if lows[i] == np.min(lows[i - swing_left:i + swing_right + 1]):
            swing_lows.append((i, lows[i]))

    last_high = None
    last_low = None
    trend = None

    for i in range(len(candles)):
        close = candles[i][4]
        volume_strength = candles[i][5] / avg_vol if avg_vol > 0 else 0.0

        if volume_strength < min_volume_strength:
            continue

        for idx, price in swing_highs:
            if idx == i:
                last_high = price

        for idx, price in swing_lows:
            if idx == i:
                last_low = price

        # ---------------- BoS / CHoCH ----------------
        if last_high and close > last_high:
            mult = (close - last_high) / last_high * 100
            if trend == "up":
                events.append({
                    "type": "bos_bullish",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(mult),
                    "volume_strength": volume_strength,
                })
            else:
                events.append({
                    "type": "choch_bullish",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(mult),
                    "volume_strength": volume_strength,
                })
                trend = "up"

        if last_low and close < last_low:
            mult = (last_low - close) / last_low * 100
            if trend == "down":
                events.append({
                    "type": "bos_bearish",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(-mult),
                    "volume_strength": volume_strength,
                })
            else:
                events.append({
                    "type": "choch_bearish",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(-mult),
                    "volume_strength": volume_strength,
                })
                trend = "down"

    return events