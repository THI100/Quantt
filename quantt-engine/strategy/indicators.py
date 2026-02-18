from typing import Dict, List

import numpy as np  # type: ignore
import utils.math as smath

# ---------------- TECHNICAL INDICATORS ----------------#

# ----------RSI-indicator----------#


def rsi(
    candles: List[List[float]],
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

    rsi_value = float(rsi_series[-1])
    rsi_mean = float(np.mean(rsi_series))

    return rsi_value, rsi_mean, rsi_series


# ----------TnK-indicator----------#


def tenkan_and_kijun(
    candles: List[List[float]],
    conversion_period: int = 9,  # Tenkan-sen
    base_period: int = 26,  # Kijun-sen
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
    tenkan_low = np.min(lows[-conversion_period:])
    tenkan_sen = (tenkan_high + tenkan_low) / 2.0

    # --- Base Line (Kijun-sen) ---
    kijun_high = np.max(highs[-base_period:])
    kijun_low = np.min(lows[-base_period:])
    kijun_sen = (kijun_high + kijun_low) / 2.0

    return tenkan_sen, kijun_sen


# ----------------------------------------------------------------------#

# ---------- MACD-indicator ----------#


def macd(
    candles: List[List[float]],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    price_mode: str = "close",  # "close" | "hl2" | "ohlc4"
):
    """
    Returns:
        macd_value: float        # last MACD line value
        signal_value: float      # last signal line value
        hist_value: float        # last histogram value
        macd_series: list[float]
        signal_series: list[float]
        hist_series: list[float]
    """

    if len(candles) < slow_period + signal_period:
        raise ValueError("Not enough candles to compute MACD")

    candles = np.asarray(candles, dtype=float)

    opens = candles[:, 1]
    highs = candles[:, 2]
    lows = candles[:, 3]
    closes = candles[:, 4]

    # --- price selection ---
    if price_mode == "close":
        price = closes
    elif price_mode == "hl2":
        price = (highs + lows) / 2.0
    elif price_mode == "ohlc4":
        price = (opens + highs + lows + closes) / 4.0
    else:
        raise ValueError("price_mode must be 'close', 'hl2', or 'ohlc4'")

    def ema(series, period):
        alpha = 2.0 / (period + 1.0)
        ema_vals = [series[0]]
        for i in range(1, len(series)):
            ema_vals.append(alpha * series[i] + (1 - alpha) * ema_vals[-1])
        return np.array(ema_vals)

    # --- MACD components ---
    ema_fast = ema(price, fast_period)
    ema_slow = ema(price, slow_period)

    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal_period)
    histogram = macd_line - signal_line

    macd_value = float(macd_line[-1])
    signal_value = float(signal_line[-1])
    hist_value = float(histogram[-1])

    return (
        macd_value,
        signal_value,
        hist_value,
        macd_line.tolist(),
        signal_line.tolist(),
        histogram.tolist(),
    )


# ----------------------------------------------------------------------#

# ---------- ATR-indicator ----------#


def atr(candles, period=14):
    trs = []
    for i in range(1, len(candles)):
        high = candles[i][2]
        low = candles[i][3]
        prev_close = candles[i - 1][4]

        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)

    return sum(trs[-period:]) / period


# ----------------------------------------------------------------------#

# ============================================================
# Candlestick Pattern Reader
# ============================================================


def detect_candlestick_patterns(
    candles: List[List[float]],
    volume_period: int = 20,
    min_volume_strength: float = 1.2,
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
                patterns.append(
                    {
                        "type": "bullish_engulfing",
                        "index": i,
                        "multiplicator": smath.clamp_multiplier(multiplier),
                        "volume_strength": volume_strength,
                    }
                )
                continue

            if curr[4] < curr[1] and prev[4] > prev[1]:
                patterns.append(
                    {
                        "type": "bearish_engulfing",
                        "index": i,
                        "multiplicator": smath.clamp_multiplier(-multiplier),
                        "volume_strength": volume_strength,
                    }
                )
                continue

        # ----------------------------------------------------
        # Hammer / Shooting Star / Hanging Man / Inverted Hammer
        # ----------------------------------------------------
        if body_c > 0:
            # Hammer / Hanging Man (long lower wick)
            if lw >= 2 * body_c and uw <= body_c:
                mult = lw / body_c
                patterns.append(
                    {
                        "type": "hammer_like",
                        "index": i,
                        "multiplicator": smath.clamp_multiplier(mult),
                        "volume_strength": volume_strength,
                    }
                )
                continue

            # Shooting Star / Inverted Hammer (long upper wick)
            if uw >= 2 * body_c and lw <= body_c:
                mult = uw / body_c
                patterns.append(
                    {
                        "type": "shooting_star_like",
                        "index": i,
                        "multiplicator": smath.clamp_multiplier(-mult),
                        "volume_strength": volume_strength,
                    }
                )
                continue

        # ----------------------------------------------------
        # Dragonfly / Gravestone Doji (wick dominance)
        # ----------------------------------------------------
        if body_c > 0:
            if lw >= 3 * body_c and uw <= body_c * 0.2:
                mult = lw / body_c
                patterns.append(
                    {
                        "type": "dragonfly_doji",
                        "index": i,
                        "multiplicator": smath.clamp_multiplier(mult),
                        "volume_strength": volume_strength,
                    }
                )
                continue

            if uw >= 3 * body_c and lw <= body_c * 0.2:
                mult = uw / body_c
                patterns.append(
                    {
                        "type": "gravestone_doji",
                        "index": i,
                        "multiplicator": smath.clamp_multiplier(-mult),
                        "volume_strength": volume_strength,
                    }
                )
                continue

        # ----------------------------------------------------
        # Doji Star (relative to previous body)
        # ----------------------------------------------------
        if body_c < body_p * 0.3 and (uw + lw) > body_p:
            mult = (uw + lw) / body_p
            sign = 1 if curr[4] > curr[1] else -1
            patterns.append(
                {
                    "type": "doji_star",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(sign * mult),
                    "volume_strength": volume_strength,
                }
            )

        # ----------------------------------------------------
        # Momentum Candle (body dominance + volume)
        # ----------------------------------------------------
        if i >= 3:
            body_1, _, _ = smath.candle_parts(candles[i - 1])
            body_2, _, _ = smath.candle_parts(candles[i - 2])
            body_3, _, _ = smath.candle_parts(candles[i - 3])

            prev_body_sum = body_1 + body_2 + body_3

            # avoid division noise
            if prev_body_sum > 0 and body_c >= 2 * prev_body_sum:
                # stricter volume requirement
                if volume_strength >= min_volume_strength:
                    mult = body_c / prev_body_sum
                    sign = 1 if curr[4] > curr[1] else -1

                    patterns.append(
                        {
                            "type": "momentum_candle",
                            "index": i,
                            "multiplicator": smath.clamp_multiplier(sign * mult),
                            "volume_strength": volume_strength,
                        }
                    )

    return patterns


# ============================================================
# Specialized Market Reader
# ============================================================


def smr(
    candles: List[List[float]],
    swing_left: int = 2,
    swing_right: int = 2,
    volume_period: int = 20,
    min_volume_strength: float = 1.1,
) -> List[Dict]:

    candles = np.asarray(candles, dtype=float)
    avg_vol = smath.average_volume(candles, volume_period)

    events = []

    highs = candles[:, 2]
    lows = candles[:, 3]
    closes = candles[:, 4]
    volumes = candles[:, 5]

    # -------- Detect swings once --------
    swing_highs = {}
    swing_lows = {}

    for i in range(swing_left, len(candles) - swing_right):
        if highs[i] == np.max(highs[i - swing_left : i + swing_right + 1]):
            swing_highs[i] = highs[i]
        if lows[i] == np.min(lows[i - swing_left : i + swing_right + 1]):
            swing_lows[i] = lows[i]

    swing_high_idxs = sorted(swing_highs.keys())
    swing_low_idxs = sorted(swing_lows.keys())

    last_high = None
    last_low = None
    prev_high = None
    prev_low = None

    trend = None
    hi_ptr = 0
    lo_ptr = 0

    for i in range(len(candles)):
        volume_strength = volumes[i] / avg_vol if avg_vol > 0 else 1.0

        # -------- advance swing pointers --------
        # We process swings as soon as they are confirmed (at index idx + swing_right).
        # We do this before the volume filter to ensure they are processed at the correct index
        # and don't cluster on the first high-volume candle.
        while (
            hi_ptr < len(swing_high_idxs) and swing_high_idxs[hi_ptr] + swing_right <= i
        ):
            idx = swing_high_idxs[hi_ptr]
            val = swing_highs[idx]
            prev_high = last_high
            last_high = val
            hi_ptr += 1

            if prev_high is not None:
                mult = (
                    abs(last_high - prev_high) / prev_high * 100
                    if prev_high != 0
                    else 0
                )
                events.append(
                    {
                        "type": "HH" if last_high > prev_high else "LH",
                        "index": i,
                        "multiplicator": smath.clamp_multiplier(mult),
                        "volume_strength": volume_strength,
                    }
                )

        while (
            lo_ptr < len(swing_low_idxs) and swing_low_idxs[lo_ptr] + swing_right <= i
        ):
            idx = swing_low_idxs[lo_ptr]
            val = swing_lows[idx]
            prev_low = last_low
            last_low = val
            lo_ptr += 1

            if prev_low is not None:
                mult = abs(last_low - prev_low) / prev_low * 100 if prev_low != 0 else 0
                events.append(
                    {
                        "type": "HL" if last_low > prev_low else "LL",
                        "index": i,
                        "multiplicator": smath.clamp_multiplier(mult),
                        "volume_strength": volume_strength,
                    }
                )

        # -------- volume filter for BOS / CHOCH --------
        if volume_strength < min_volume_strength:
            continue

        close = closes[i]

        # -------- Initialize trend --------
        if trend is None and last_high and last_low:
            trend = "up" if close > last_high else "down"
            continue

        # -------- BOS / CHOCH --------
        if last_high and close > last_high:
            event_type = "bos_bullish" if trend == "up" else "choch_bullish"
            mult = (close - last_high) / last_high * 100

            events.append(
                {
                    "type": event_type,
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(mult),
                    "volume_strength": volume_strength,
                }
            )
            trend = "up"

        if last_low and close < last_low:
            event_type = "bos_bearish" if trend == "down" else "choch_bearish"
            mult = (last_low - close) / last_low * 100

            events.append(
                {
                    "type": event_type,
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(mult),
                    "volume_strength": volume_strength,
                }
            )
            trend = "down"

    return events
