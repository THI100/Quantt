import numpy as np
from data import cache  # [(ts, open, high, low, close), ...] length = 42
from typing import Dict, List

#----------------------------------------------------------------------#

#---------------- TECHNICAL INDICATORS ----------------#

#----------RSI-indicator----------#

def rsi(
    candles=cache.cached_p42,
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

    return rsi_value, rsi_mean

#----------TnK-indicator----------#

def tenkan_and_kijun(
    candles=cache.cached_p42,
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

#---------------- CANDLESTICK PATTERNS ----------------#

# ---------- helpers ----------
def average_volume(candles: np.ndarray, period: int = 20) -> float:
    vols = candles[-period:, 5]
    return float(vols.mean())


def candle_parts(c):
    o, h, l, c_ = c[1], c[2], c[3], c[4]
    body = abs(c_ - o)
    upper_wick = h - max(o, c_)
    lower_wick = min(o, c_) - l
    return body, upper_wick, lower_wick


# ---------- pattern checks ----------
def engulfing(prev, curr):
    prev_body, _, _ = candle_parts(prev)
    curr_body, _, _ = candle_parts(curr)

    if curr_body >= 2 * prev_body:
        # bullish
        if curr[4] > curr[1] and prev[4] < prev[1]:
            return {"type": "bullish_engulfing", "multiplier": curr_body / prev_body}
        # bearish
        if curr[4] < curr[1] and prev[4] > prev[1]:
            return {"type": "bearish_engulfing", "multiplier": -(curr_body / prev_body)}
    return None


def dragonfly_gravestone(c):
    body, uw, lw = candle_parts(c)
    if body == 0:
        body = 1e-9

    if lw >= 2 * body and uw <= body * 0.2:
        return "dragonfly_doji"
    if uw >= 2 * body and lw <= body * 0.2:
        return "gravestone_doji"
    return None


def hammer_shooting_star(c):
    body, uw, lw = candle_parts(c)
    if body == 0:
        return None

    if lw >= 2 * body and uw <= body:
        return "hammer"
    if uw >= 2 * body and lw <= body:
        return "shooting_star"
    return None


def hanging_man_inverted_hammer(c, trend="up"):
    body, uw, lw = candle_parts(c)
    if body == 0:
        return None

    if trend == "up" and lw >= 2 * body:
        return "hanging_man"
    if trend == "down" and uw >= 2 * body:
        return "inverted_hammer"
    return None


def doji_star(prev, curr):
    prev_body, _, _ = candle_parts(prev)
    body, uw, lw = candle_parts(curr)

    if body < prev_body * 0.3 and (uw + lw) > prev_body:
        if curr[4] > curr[1]:
            return "bullish_doji_star"
        else:
            return "bearish_doji_star"
    return None


# ---------- rolling detector ----------
def detect_candlestick_patterns(
    candles=cache.cached_p42,
    volume_period: int = 20,
) -> List[Dict]:

    candles = np.asarray(candles, dtype=float)
    avg_vol = average_volume(candles, volume_period)

    patterns = []

    for i in range(1, len(candles)):
        prev = candles[i - 1]
        curr = candles[i]

        strength = curr[5] / avg_vol if avg_vol > 0 else 1.0

        e = engulfing(prev, curr)
        if e:
            patterns.append({**e, "index": i, "volume_strength": strength})

        d = dragonfly_gravestone(curr)
        if d:
            patterns.append({"type": d, "index": i, "volume_strength": strength})

        h = hammer_shooting_star(curr)
        if h:
            patterns.append({"type": h, "index": i, "volume_strength": strength})

        s = doji_star(prev, curr)
        if s:
            patterns.append({"type": s, "index": i, "volume_strength": strength})

    return patterns

#----------------------------------------------------------------------#

# ---------- helpers ----------
def swing_points(candles: np.ndarray, left: int = 2, right: int = 2):
    highs = candles[:, 2]
    lows = candles[:, 3]

    swing_highs = []
    swing_lows = []

    for i in range(left, len(candles) - right):
        if highs[i] == np.max(highs[i - left:i + right + 1]):
            swing_highs.append((i, highs[i]))
        if lows[i] == np.min(lows[i - left:i + right + 1]):
            swing_lows.append((i, lows[i]))

    return swing_highs, swing_lows


def average_volume(candles: np.ndarray, period: int = 20) -> float:
    return float(candles[-period:, 5].mean())


# ---------- SMC core ----------
def smc_reader(
    candles=cache.cached_p42,
    swing_left: int = 2,
    swing_right: int = 2,
    volume_period: int = 20,
) -> List[Dict]:
    """
    Detects:
        - FVG (Fair Value Gap)
        - BoS (Break of Structure)
        - CHoCH (Change of Character)

    Returns list of events.
    """

    candles = np.asarray(candles, dtype=float)
    avg_vol = average_volume(candles, volume_period)

    swing_highs, swing_lows = swing_points(candles, swing_left, swing_right)

    events = []

    # ---------- FVG ----------
    for i in range(2, len(candles)):
        c1, c2, c3 = candles[i - 2], candles[i - 1], candles[i]

        # Bullish FVG
        if c3[3] > c1[2]:
            events.append({
                "type": "bullish_fvg",
                "index": i,
                "gap": (c1[2], c3[3]),
                "volume_strength": c2[5] / avg_vol
            })

        # Bearish FVG
        if c3[2] < c1[3]:
            events.append({
                "type": "bearish_fvg",
                "index": i,
                "gap": (c3[2], c1[3]),
                "volume_strength": c2[5] / avg_vol
            })

    # ---------- BoS & CHoCH ----------
    last_high = None
    last_low = None
    trend = None  # "up" | "down"

    for i in range(len(candles)):
        high = candles[i][2]
        low = candles[i][3]
        close = candles[i][4]
        vol_strength = candles[i][5] / avg_vol

        # update structure levels
        for idx, price in swing_highs:
            if idx == i:
                last_high = price

        for idx, price in swing_lows:
            if idx == i:
                last_low = price

        # BoS up
        if last_high and close > last_high:
            if trend == "up":
                events.append({
                    "type": "bos_bullish",
                    "index": i,
                    "level": last_high,
                    "volume_strength": vol_strength
                })
            else:
                events.append({
                    "type": "choch_bullish",
                    "index": i,
                    "level": last_high,
                    "volume_strength": vol_strength
                })
                trend = "up"

        # BoS down
        if last_low and close < last_low:
            if trend == "down":
                events.append({
                    "type": "bos_bearish",
                    "index": i,
                    "level": last_low,
                    "volume_strength": vol_strength
                })
            else:
                events.append({
                    "type": "choch_bearish",
                    "index": i,
                    "level": last_low,
                    "volume_strength": vol_strength
                })
                trend = "down"

    return events
