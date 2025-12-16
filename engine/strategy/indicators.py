import numpy as np
from data.cache import cached_p14  # [(ts, open, high, low, close), ...] length = 14

def rsi(
    candles=cached_p14,
    period: int = 14,
    mode: str = "close-close",  # "close-close" (standard) | "open-close"
):
    """
    Returns:
        rsi_value: float
        rsi_mean:  float
    """

    if len(candles) < period:
        raise ValueError("Not enough candles")

    candles = np.asarray(candles, dtype=float)

    opens = candles[:, 1]
    closes = candles[:, 4]

    # --- price deltas ---
    if mode == "close-close":
        # Standard RSI (Wilder)
        deltas = np.diff(closes)
    elif mode == "open-close":
        # Candle body momentum
        deltas = closes - opens
    else:
        raise ValueError("mode must be 'close-close' or 'open-close'")

    # --- gains / losses ---
    gains = np.clip(deltas, 0.0, None)
    losses = np.clip(-deltas, 0.0, None)

    # --- average gain / loss ---
    avg_gain = gains.mean()
    avg_loss = losses.mean()

    # --- RS & RSI ---
    if avg_loss == 0:
        rsi_value = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi_value = 100.0 - (100.0 / (1.0 + rs))

    # With exactly 14 candles, RSI is a single value

    return rsi_value
