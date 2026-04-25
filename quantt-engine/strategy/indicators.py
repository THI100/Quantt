from typing import Dict, List

import numpy as np  # type: ignore
from loguru import logger

import utils.math as smath

# ---------------- TECHNICAL INDICATORS ---------------- #

# ---------- VWAP-indicator ----------#

def vwap(
    candles: List[List[float]],
    period: int = 14,
    use_typical_price: bool = True
):
    """
    Returns:
        vwap_value: float   # last VWAP value
        vwap_mean:  float   # mean VWAP over the window
        vwap_series: list   # full series of VWAP values
    """
    if len(candles) < period:
        logger.warning("Not enough candles to compute VWAP")

    candles = np.asarray(candles, dtype=float)

    # OHLC structure
    highs = candles[:, 2]
    lows = candles[:, 3]
    closes = candles[:, 4]
    volumes = candles[:, 5]

    if use_typical_price:
        prices = (highs + lows + closes) / 3
    else:
        prices = closes

    pv = prices * volumes
    vwap_series = []

    # Sliding window calculation (non-vectorized)
    for i in range(period, len(candles) + 1):
        window_pv = pv[i-period:i]
        window_vol = volumes[i-period:i]

        sum_vol = np.sum(window_vol)

        if sum_vol == 0:
            current_vwap = prices[i-1]
        else:
            current_vwap = np.sum(window_pv) / sum_vol

        vwap_series.append(current_vwap)

    vwap_value = float(vwap_series[-1])
    vwap_mean = float(np.mean(vwap_series))

    return vwap_value, vwap_mean, vwap_series


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
        logger.warning("Not enough candles to compute RSI")

    candles = np.asarray(candles, dtype=float)

    opens = candles[:, 1]
    closes = candles[:, 4]

    # --- price deltas ---
    if mode == "close-close":
        deltas = np.diff(closes)
    elif mode == "open-close":
        deltas = closes - opens
    else:
        logger.error(f"mode must be 'close-close' or 'open-close', actual mode: {mode}")

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
        logger.warning("Not enough candles for tenkan and kijun.")

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
        logger.warning("Not enough candles to compute MACD")

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
        logger.error(
            f"price_mode must be 'close', 'hl2', or 'ohlc4' actual price_mode: {price_mode}"
        )

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


# ---------- EMA-indicator ----------#


def ema(
    candles: List[List[float]],
    period: int = 20
):
    """
    Returns:
        ema_value: float   # last EMA value
        ema_mean:  float   # mean EMA over the window
        ema_series: list   # full series of EMA values
    """
    if len(candles) < period:
        logger.warning("Not enough candles to compute EMA")
        return 0.0, 0.0, []

    candles = np.asarray(candles, dtype=float)
    closes = candles[:, 4]

    ema_series = []

    # Initialize with the SMA of the first 'period' candles
    current_ema = np.mean(closes[:period])
    ema_series.append(current_ema)

    # Calculate the smoothing multiplier
    multiplier = 2 / (period + 1)

    # Calculate remaining EMA values
    for i in range(period, len(closes)):
        current_ema = (closes[i] - current_ema) * multiplier + current_ema
        ema_series.append(current_ema)

    ema_value = float(ema_series[-1])
    ema_mean = float(np.mean(ema_series))

    return ema_value, ema_mean, ema_series


# ---------- ATR-indicator ----------#


def atr(
    candles: List[List[float]],
    period: int = 14
) -> Tuple[float, float, list]:
    """
    Returns:
        atr_value: float    # last ATR value
        atr_mean:  float    # mean ATR over the window
        atr_series: list    # full series of ATR values
    """
    if len(candles) < period + 1:
        logger.warning("Not enough candles to compute ATR")
        return 0.0, 0.0, []

    candles = np.asarray(candles, dtype=float)
    highs = candles[:, 2]
    lows = candles[:, 3]
    closes = candles[:, 4]

    tr1 = highs[1:] - lows[1:]
    tr2 = np.abs(highs[1:] - closes[:-1])
    tr3 = np.abs(lows[1:] - closes[:-1])

    tr = np.maximum(tr1, np.maximum(tr2, tr3))

    # The first ATR value is the SMA of the first 'period' TRs
    atr_series = []
    current_atr = np.mean(tr[:period])
    atr_series.append(current_atr)

    # Subsequent values use Wilder's: (Prev_ATR * (n-1) + Current_TR) / n
    for i in range(period, len(tr)):
        current_atr = (current_atr * (period - 1) + tr[i]) / period
        atr_series.append(current_atr)

    atr_value = float(atr_series[-1])
    atr_mean = float(np.mean(atr_series))

    return atr_value, atr_mean, atr_series


# ---------- ROC-indicator ----------#


def roc(
    candles: List[List[float]],
    period: int = 12
):
    """
    Returns:
        roc_value: float   # last ROC value (percentage)
        roc_mean:  float   # mean ROC over the window
        roc_series: list   # full series of ROC values
    """
    if len(candles) < period + 1:
        logger.warning("Not enough candles to compute ROC")
        return 0.0, 0.0, []

    candles = np.asarray(candles, dtype=float)
    closes = candles[:, 4]

    # Calculate ROC: ((Current - Past) / Past) * 100
    # We slice to align the 'current' with the 'past'
    current_prices = closes[period:]
    past_prices = closes[:-period]

    roc_series = ((current_prices - past_prices) / past_prices) * 100

    roc_value = float(roc_series[-1])
    roc_mean = float(np.mean(roc_series))

    return roc_value, roc_mean, roc_series.tolist()


# ---------- ST-indicator ----------#


def supertrend(
    candles: List[List[float]],
    period: int = 10,
    multiplier: float = 3.0
) -> Tuple[float, str, list]:
    """
    Returns:
        last_st: float      # Latest SuperTrend value
        last_dir: str       # Current direction ("up" | "down")
        st_series: list     # Full series of SuperTrend values
    """
    if len(candles) <= period:
        logger.warning("Not enough candles for SuperTrend")
        return 0.0, "neutral", []

    candles = np.asarray(candles, dtype=float)
    highs = candles[:, 2]
    lows = candles[:, 3]
    closes = candles[:, 4]

    # 1. Calculate ATR rolling window
    atr_values = np.zeros(len(candles))
    for i in range(1, len(candles)):
        tr = max(highs[i] - lows[i],
                 abs(highs[i] - closes[i-1]),
                 abs(lows[i] - closes[i-1]))
        atr_values[i] = tr

    # Simple Moving Average of TR to get ATR
    # We'll use a manual rolling mean to stay consistent with your ATR function
    def get_atr_at_index(idx):
        return np.mean(atr_values[max(1, idx-period+1):idx+1])

    # 2. Initialize variables
    st_series = [0.0] * len(candles)
    direction = [1] * len(candles) # 1 for Up, -1 for Down

    upper_band = np.zeros(len(candles))
    lower_band = np.zeros(len(candles))

    for i in range(period, len(candles)):
        current_atr = get_atr_at_index(i)
        median_price = (highs[i] + lows[i]) / 2

        basic_ub = median_price + (multiplier * current_atr)
        basic_lb = median_price - (multiplier * current_atr)

        # Final Upper Band (Cannot move up if price is below previous upper band)
        if basic_ub < upper_band[i-1] or closes[i-1] > upper_band[i-1]:
            upper_band[i] = basic_ub
        else:
            upper_band[i] = upper_band[i-1]

        # Final Lower Band (Cannot move down if price is above previous lower band)
        if basic_lb > lower_band[i-1] or closes[i-1] < lower_band[i-1]:
            lower_band[i] = basic_lb
        else:
            lower_band[i] = lower_band[i-1]

        # Determine Direction
        if closes[i] > upper_band[i-1]:
            direction[i] = 1
        elif closes[i] < lower_band[i-1]:
            direction[i] = -1
        else:
            direction[i] = direction[i-1]

        st_series[i] = lower_band[i] if direction[i] == 1 else upper_band[i]

    last_st = float(st_series[-1])
    last_dir = "up" if direction[-1] == 1 else "down"

    return last_st, last_dir, st_series[period:]


# ---------- BB-indicator ----------#


def bollinger_bands(
    candles: List[List[float]],
    period: int = 20,
    std_dev_multiplier: float = 2.0
):
    """
    Returns:
        last_bands: tuple   # (upper, middle, lower) for the latest candle
        bb_mean_width: float # mean bandwidth (volatility proxy)
        bb_series: dict     # full series for upper, middle, and lower
    """
    if len(candles) < period:
        logger.warning("Not enough candles to compute Bollinger Bands")

    candles = np.asarray(candles, dtype=float)
    closes = candles[:, 4]

    upper_series = []
    middle_series = []
    lower_series = []
    bandwidth_series = []

    for i in range(period, len(closes) + 1):
        window = closes[i-period:i]

        sma = np.mean(window)
        std = np.std(window)

        upper = sma + (std_dev_multiplier * std)
        lower = sma - (std_dev_multiplier * std)

        upper_series.append(upper)
        middle_series.append(sma)
        lower_series.append(lower)

        # Bandwidth is a useful secondary metric: (Upper - Lower) / Middle
        bandwidth_series.append((upper - lower) / sma)

    last_bands = (float(upper_series[-1]), float(middle_series[-1]), float(lower_series[-1]))
    bb_mean_width = float(np.mean(bandwidth_series))

    bb_series = {
        "upper": upper_series,
        "middle": middle_series,
        "lower": lower_series
    }

    return last_bands, bb_mean_width, bb_series


# ---------- ADX-indicator ----------#


def adx(
    candles: List[List[float]],
    period: int = 14
):
    """
    Returns:
        adx_value: float    # last ADX value
        adx_mean: float     # mean ADX strength
        adx_series: list    # full ADX series
    """
    if len(candles) < period * 2:
        logger.warning("Not enough candles to compute ADX")

    candles = np.asarray(candles, dtype=float)
    highs = candles[:, 2]
    lows = candles[:, 3]
    closes = candles[:, 4]

    # Calculate True Range (TR) and Directional Movement (DM)
    up_move = np.diff(highs)
    down_move = -np.diff(lows)

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    # Simplified True Range calculation
    tr = np.maximum(highs[1:] - lows[1:], np.abs(highs[1:] - closes[:-1]))
    tr = np.maximum(tr, np.abs(lows[1:] - closes[:-1]))

    # Wilder's Smoothing
    def smooth(data, per):
        smoothed = np.zeros(len(data))
        smoothed[per-1] = np.mean(data[:per])
        for i in range(per, len(data)):
            smoothed[i] = (smoothed[i-1] * (per - 1) + data[i]) / per
        return smoothed

    tr_smooth = smooth(tr, period)
    plus_di = 100 * (smooth(plus_dm, period) / tr_smooth)
    minus_di = 100 * (smooth(minus_dm, period) / tr_smooth)

    # Calculate DX and ADX
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10) # 1e-10 to avoid div by zero
    adx_series = smooth(dx, period)

    adx_value = float(adx_series[-1])
    adx_mean = float(np.mean(adx_series))

    return adx_value, adx_mean, adx_series.tolist()


# ---------- ATR-indicator ----------#


def obv(
    candles: List[List[float]]
):
    """
    Returns:
        obv_value: float    # last OBV value
        obv_mean:  float    # mean OBV over the series
        obv_series: list    # full OBV series
    """
    if len(candles) < 2:
        logger.warning("Not enough candles to compute OBV")

    candles = np.asarray(candles, dtype=float)

    closes = candles[:, 4]
    volumes = candles[:, 5]

    # Calculate price changes
    # We use np.diff and then pad with a 0 at the start to keep arrays same length
    price_change = np.diff(closes)
    price_change = np.insert(price_change, 0, 0)

    # Determine direction: +1 if price up, -1 if price down, 0 if flat
    direction = np.sign(price_change)

    # Cumulative sum of (direction * volume)
    obv_series = np.cumsum(direction * volumes)

    obv_value = float(obv_series[-1])
    obv_mean = float(np.mean(obv_series))

    return obv_value, obv_mean, obv_series.tolist()


# --------------------- STRUCTURAL INDICATORS --------------------- #

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
    min_fvg_size: float = 0.0, # Minimum % size of the gap to be recorded
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

        # -------- FVG Detection (Requires at least 3 candles) --------
        if i >= 2:
            # Bullish FVG: Low of candle[i] > High of candle[i-2]
            if lows[i] > highs[i - 2]:
                gap_size = (lows[i] - highs[i - 2]) / highs[i - 2] * 100
                if gap_size > min_fvg_size:
                    events.append({
                        "type": "fvg_bullish",
                        "index": i,
                        "top": lows[i],
                        "bottom": highs[i - 2],
                        "multiplicator": smath.clamp_multiplier(gap_size),
                        "volume_strength": volume_strength,
                    })

            # Bearish FVG: High of candle[i] < Low of candle[i-2]
            elif highs[i] < lows[i - 2]:
                gap_size = (lows[i - 2] - highs[i]) / lows[i - 2] * 100
                if gap_size > min_fvg_size:
                    events.append({
                        "type": "fvg_bearish",
                        "index": i,
                        "top": lows[i - 2],
                        "bottom": highs[i],
                        "multiplicator": smath.clamp_multiplier(gap_size),
                        "volume_strength": volume_strength,
                    })

        # -------- advance swing pointers --------
        while (
            hi_ptr < len(swing_high_idxs) and swing_high_idxs[hi_ptr] + swing_right <= i
        ):
            idx = swing_high_idxs[hi_ptr]
            val = swing_highs[idx]
            prev_high = last_high
            last_high = val
            hi_ptr += 1

            if prev_high is not None:
                mult = abs(last_high - prev_high) / prev_high * 100 if prev_high != 0 else 0
                events.append({
                    "type": "HH" if last_high > prev_high else "LH",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(mult),
                    "volume_strength": volume_strength,
                })

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
                events.append({
                    "type": "HL" if last_low > prev_low else "LL",
                    "index": i,
                    "multiplicator": smath.clamp_multiplier(mult),
                    "volume_strength": volume_strength,
                })

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
            events.append({
                "type": event_type,
                "index": i,
                "multiplicator": smath.clamp_multiplier(mult),
                "volume_strength": volume_strength,
            })
            trend = "up"

        if last_low and close < last_low:
            event_type = "bos_bearish" if trend == "down" else "choch_bearish"
            mult = (last_low - close) / last_low * 100
            events.append({
                "type": event_type,
                "index": i,
                "multiplicator": smath.clamp_multiplier(mult),
                "volume_strength": volume_strength,
            })
            trend = "down"

    return events


# ============================================================
# Pivot Points Fibonacci
# ============================================================


def pivot_points_fibonacci(
    candles: List[List[float]]
) -> Dict[str, float]:
    """
    Calculates Fibonacci Pivot Points based on the most recent completed period.
    Typically used with Daily candles to find levels for the next day.

    Returns:
        levels: dict  # Contains PP, R1-R3, and S1-S3
    """
    if len(candles) < 1:
        logger.warning("Not enough data to compute Pivot Points")
        return {}

    # Use the most recent candle (index -1)
    last_candle = np.asarray(candles[-1], dtype=float)

    high = last_candle[2]
    low = last_candle[3]
    close = last_candle[4]

    pivot_range = high - low
    pp = (high + low + close) / 3

    levels = {
        "pp": float(pp),
        "r1": float(pp + (pivot_range * 0.382)),
        "r2": float(pp + (pivot_range * 0.618)),
        "r3": float(pp + (pivot_range * 1.000)),
        "s1": float(pp - (pivot_range * 0.382)),
        "s2": float(pp - (pivot_range * 0.618)),
        "s3": float(pp - (pivot_range * 1.000))
    }

    return levels
