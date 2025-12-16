import numpy as np
from data.cache import cached_p42  # [(ts, open, high, low, close), ...] length = 42

#----------------------------------------------------------------------#

def rsi(
    candles=cached_p42,
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

#----------------------------------------------------------------------#

def tenkan_and_kijun(
    candles=cached_p42,
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

def _body(o, c):
    return abs(c - o)

def _upper_wick(o, h, c):
    return h - max(o, c)

def _lower_wick(o, l, c):
    return min(o, c) - l


# ---------------- ENGULFING ----------------
def engulfing(candles):
    if len(candles) < 2:
        return None

    _, o1, _, _, c1 = candles[-2]
    _, o2, _, _, c2 = candles[-1]

    body1 = _body(o1, c1)
    body2 = _body(o2, c2)

    if body1 == 0:
        return None

    if body2 >= 2 * body1:
        direction = 1 if c2 > o2 else -1
        multiplier = body2 / body1
        return direction * multiplier

    return None


# ---------------- DOJI TYPES ----------------
def dragonfly_doji(candle, tol=0.1):
    _, o, h, l, c = candle
    body = _body(o, c)
    return body <= tol * (h - l) and _upper_wick(o, h, c) <= body

def gravestone_doji(candle, tol=0.1):
    _, o, h, l, c = candle
    body = _body(o, c)
    return body <= tol * (h - l) and _lower_wick(o, l, c) <= body


# ---------------- HAMMER / SHOOTING STAR ----------------
def hammer(candle):
    _, o, h, l, c = candle
    body = _body(o, c)
    return _lower_wick(o, l, c) >= 2 * body and _upper_wick(o, h, c) <= body

def shooting_star(candle):
    _, o, h, l, c = candle
    body = _body(o, c)
    return _upper_wick(o, h, c) >= 2 * body and _lower_wick(o, l, c) <= body


# ---------------- DOJI STARS ----------------
def bullish_doji_star(candles):
    if len(candles) < 2:
        return False

    prev = candles[-2]
    curr = candles[-1]

    prev_body = _body(prev[1], prev[4])
    curr_body = _body(curr[1], curr[4])

    wick_sum = (
        _upper_wick(curr[1], curr[2], curr[4]) +
        _lower_wick(curr[1], curr[3], curr[4])
    )

    return curr_body < prev_body and wick_sum > prev_body and curr[4] > curr[1]

def bearish_doji_star(candles):
    if len(candles) < 2:
        return False

    prev = candles[-2]
    curr = candles[-1]

    prev_body = _body(prev[1], prev[4])
    curr_body = _body(curr[1], curr[4])

    wick_sum = (
        _upper_wick(curr[1], curr[2], curr[4]) +
        _lower_wick(curr[1], curr[3], curr[4])
    )

    return curr_body < prev_body and wick_sum > prev_body and curr[4] < curr[1]


# ---------------- HANGING MAN / INVERTED HAMMER ----------------
def hanging_man(candle):
    # same geometry as hammer, context-dependent (uptrend)
    return hammer(candle)

def inverted_hammer(candle):
    # same geometry as shooting star, context-dependent (downtrend)
    return shooting_star(candle)


# ---------------- AGGREGATOR ----------------
def candlestick_patterns(candles):
    last = candles[-1]

    return {
        "engulfing": engulfing(candles),
        "dragonfly_doji": dragonfly_doji(last),
        "gravestone_doji": gravestone_doji(last),
        "hammer": hammer(last),
        "shooting_star": shooting_star(last),
        "bullish_doji_star": bullish_doji_star(candles),
        "bearish_doji_star": bearish_doji_star(candles),
        "hanging_man": hanging_man(last),
        "inverted_hammer": inverted_hammer(last),
    }
