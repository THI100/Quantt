import numpy as np

# -------------------------------- Helpers ----------------------------------------- #

def average_volume(candles: np.ndarray, period: int = 20) -> float:
    vols = candles[-period:, 5]
    return float(vols.mean())


def candle_parts(c):
    o, h, l, c_ = c[1], c[2], c[3], c[4]
    body = abs(c_ - o)
    upper_wick = h - max(o, c_)
    lower_wick = min(o, c_) - l
    return body, upper_wick, lower_wick

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

def clamp_multiplier(value: float, min_v: float = -25.0, max_v: float = 25.0) -> float:
    return float(np.clip(value, min_v, max_v))

def scale_0_100(value: float, max_value: float) -> float:
    return round(min(abs(value) / max_value, 1.0) * 100, 2)
