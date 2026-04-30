import math

import numpy as np
from loguru import logger

import strategy.indicators as indicators
from config import risk
from data import cache
from data.cache import cached_p14
from utils.math import scale_0_100

r = risk.watcher.get_config()

# ----------------------- Helpers ----------------------- #


def _check_nan(value, name: str):
    """Raise ValueError if value is None, NaN, or infinite."""
    if value is None:
        raise ValueError(f"Indicator '{name}' returned None.")
    try:
        if math.isnan(value) or math.isinf(value):
            raise ValueError(f"Indicator '{name}' returned an invalid value: {value}")
    except TypeError:
        raise ValueError(f"Indicator '{name}' returned a non-numeric value: {value!r}")
    return value


# --------------------- Auxiliaries --------------------- #


def get_signal_candlestick_patterns(market: str):
    candles = cache.cached_p14(market=market)
    patterns = indicators.detect_candlestick_patterns(candles=candles)

    m_force_bull, m_force_bear = 0.0, 0.0
    conf_bull, conf_bear = 0, 0
    total_len = len(candles)

    for p in patterns:
        mult = p["multiplicator"]
        # Linear time decay: more recent patterns have more weight
        recency_weight = p["index"] / total_len if total_len > 0 else 1.0
        impact = abs(mult) * min(p["volume_strength"], 2.0) * recency_weight

        if mult > 0:
            m_force_bull += impact
            conf_bull += 1
        elif mult < 0:
            m_force_bear += impact
            conf_bear += 1

    return m_force_bull, m_force_bear, conf_bull, conf_bear


def get_signal_smr(market: str):
    candles = cache.cached_p42(market=market)
    smr_events = indicators.smr(candles=candles)

    m_force_bull, m_force_bear = 0.0, 0.0
    conf_bull, conf_bear = 0, 0
    total_len = len(candles)

    # Weight config for easier tuning
    WEIGHTS = {
        "bos_bullish": 1.5,
        "bos_bearish": 1.5,
        "choch_bullish": 2.0,
        "choch_bearish": 2.0,
        "fvg_bullish": 0.7,
        "fvg_bearish": 0.7,
    }

    for e in smr_events:
        etype = e["type"]
        if etype not in WEIGHTS:
            continue

        weight = WEIGHTS[etype]
        # Decay factor: makes older SMR events less relevant than fresh breakouts
        recency_weight = e["index"] / total_len if total_len > 0 else 1.0
        impact = (
            abs(e["multiplicator"])
            * min(e["volume_strength"], 2.0)
            * weight
            * recency_weight
        )

        if "bullish" in etype:
            conf_bull += 1
            m_force_bull += impact
            if etype == "choch_bullish":
                m_force_bear *= 0.5  # Dampen bearish force on trend reversal

        elif "bearish" in etype:
            conf_bear += 1
            m_force_bear += impact
            if etype == "choch_bearish":
                m_force_bull *= 0.5  # Dampen bullish force on trend reversal

    return m_force_bull, m_force_bear, conf_bull, conf_bear


# --------------------- FINAL AVALIATION --------------------- #


def avaliation_of_market(Market: str, parameters: list[str]) -> dict:
    candles = cache.cached_p42(market=Market)

    bull_votes = 0
    bear_votes = 0
    total_signals = 0

    category_scores = {"trend": [], "momentum": [], "volume": [], "structure": []}

    adx_val = 20.0
    atr_ratio = 0.5

    parameters_lower = [p.lower() for p in parameters]

    if "vwap" in parameters_lower:
        vwap_value, vwap_mean, vwap_series = indicators.vwap(candles)
        _check_nan(vwap_value, "vwap_value")
        _check_nan(vwap_mean, "vwap_mean")
        score = 1.0 if vwap_value > vwap_mean else 0.0
        category_scores["trend"].append(score)
        if score > 0.5:
            bull_votes += 1
        else:
            bear_votes += 1
        total_signals += 1

    if "rsi" in parameters_lower:
        rsi_value, rsi_mean, rsi_series = indicators.rsi(candles)
        _check_nan(rsi_value, "rsi_value")
        score = rsi_value / 100.0
        category_scores["momentum"].append(score)
        if rsi_value > 50:
            bull_votes += 1
        else:
            bear_votes += 1
        total_signals += 1

    if "tnk" in parameters_lower:
        tenkan_sen, kijun_sen = indicators.tenkan_and_kijun(candles)
        _check_nan(tenkan_sen, "tenkan_sen")
        _check_nan(kijun_sen, "kijun_sen")
        score = 1.0 if tenkan_sen > kijun_sen else 0.0
        category_scores["trend"].append(score)
        if score > 0.5:
            bull_votes += 1
        else:
            bear_votes += 1
        total_signals += 1

    if "macd" in parameters_lower:
        (
            macd_value,
            signal_value,
            hist_value,
            macd_series,
            signal_series,
            hist_series,
        ) = indicators.macd(candles)
        _check_nan(hist_value, "macd_hist_value")
        score = 1.0 if hist_value > 0 else 0.0
        category_scores["momentum"].append(score)
        if hist_value > 0:
            bull_votes += 1
        else:
            bear_votes += 1
        total_signals += 1

    if "ema" in parameters_lower:
        ema_value, ema_mean, ema_series = indicators.ema(candles)
        _check_nan(ema_value, "ema_value")
        _check_nan(ema_mean, "ema_mean")
        score = 1.0 if ema_value > ema_mean else 0.0
        category_scores["trend"].append(score)
        if score > 0.5:
            bull_votes += 1
        else:
            bear_votes += 1
        total_signals += 1

    if "atr" in parameters_lower:
        atr_value, atr_mean, atr_series = indicators.atr(candles)
        _check_nan(atr_value, "atr_value")
        _check_nan(atr_mean, "atr_mean")
        atr_ratio = min(atr_value / (atr_mean + 1e-9), 1.0)
        category_scores["structure"].append(atr_ratio)

    if "roc" in parameters_lower:
        roc_value, roc_mean, roc_series = indicators.roc(candles)
        _check_nan(roc_value, "roc_value")
        score = 1.0 if roc_value > 0 else 0.0
        category_scores["momentum"].append(score)
        if roc_value > 0:
            bull_votes += 1
        else:
            bear_votes += 1
        total_signals += 1

    if "st" in parameters_lower:
        last_st, last_dir, st_series = indicators.supertrend(candles)
        if not isinstance(last_dir, str):
            raise ValueError(
                f"Indicator 'supertrend_dir' returned a non-string value: {last_dir!r}"
            )
        score = 1.0 if last_dir == "up" else 0.0
        category_scores["trend"].append(score)
        if last_dir == "up":
            bull_votes += 1
        else:
            bear_votes += 1
        total_signals += 1

    if "bb" in parameters_lower:
        last_bands, bb_mean_width, bb_series = indicators.bollinger_bands(candles)
        upper, middle, lower = last_bands
        _check_nan(upper, "bb_upper")
        _check_nan(middle, "bb_middle")
        _check_nan(lower, "bb_lower")
        _check_nan(bb_mean_width, "bb_mean_width")
        bb_width = upper - lower
        squeeze_ratio = min(bb_width / (bb_mean_width + 1e-9), 1.0)
        category_scores["structure"].append(squeeze_ratio)

    if "adx" in parameters_lower:
        adx_value, adx_mean, adx_series = indicators.adx(candles)
        _check_nan(adx_value, "adx_value")
        _check_nan(adx_mean, "adx_mean")
        adx_val = adx_value
        score = min(adx_value / 50.0, 1.0)
        category_scores["trend"].append(score)

    if "obv" in parameters_lower:
        obv_value, obv_mean, obv_series = indicators.obv(candles)
        _check_nan(obv_value, "obv_value")
        _check_nan(obv_mean, "obv_mean")
        score = 1.0 if obv_value > obv_mean else 0.0
        category_scores["volume"].append(score)
        if obv_value > obv_mean:
            bull_votes += 1
        else:
            bear_votes += 1
        total_signals += 1

    if "dscp" in parameters_lower:
        m_force_bull, m_force_bear, conf_bull, conf_bear = (
            get_signal_candlestick_patterns(Market)
        )
        _check_nan(m_force_bull, "dscp_m_force_bull")
        _check_nan(m_force_bear, "dscp_m_force_bear")
        _check_nan(conf_bull, "dscp_conf_bull")
        _check_nan(conf_bear, "dscp_conf_bear")
        if m_force_bull > m_force_bear:
            bull_votes += 1
            category_scores["structure"].append(min(m_force_bull + conf_bull, 1.0))
        elif m_force_bear > m_force_bull:
            bear_votes += 1
            category_scores["structure"].append(
                max(0.0, 1.0 - (m_force_bear + conf_bear))
            )
        total_signals += 1

    if "smr" in parameters_lower:
        m_force_bull, m_force_bear, conf_bull, conf_bear = get_signal_smr(Market)
        _check_nan(m_force_bull, "smr_m_force_bull")
        _check_nan(m_force_bear, "smr_m_force_bear")
        _check_nan(conf_bull, "smr_conf_bull")
        _check_nan(conf_bear, "smr_conf_bear")
        if m_force_bull > m_force_bear:
            bull_votes += 1
            category_scores["structure"].append(min(m_force_bull + conf_bull, 1.0))
        elif m_force_bear > m_force_bull:
            bear_votes += 1
            category_scores["structure"].append(
                max(0.0, 1.0 - (m_force_bear + conf_bear))
            )
        total_signals += 1

    # Aggregate results
    direction = "neutral"
    confidence = 0.50

    if total_signals > 0:
        if bull_votes > bear_votes:
            direction = "buy"
            confidence = round(bull_votes / total_signals, 2)
        elif bear_votes > bull_votes:
            direction = "sell"
            confidence = round(bear_votes / total_signals, 2)
        else:
            direction = "neutral"
            confidence = 0.50

    regime = "trend" if adx_val >= 25.0 else "range"

    strength = (
        round(min(adx_val / 50.0, 1.0), 2)
        if "adx" in parameters_lower
        else round(atr_ratio, 2)
    )

    grades = {}
    for cat, scores in category_scores.items():
        grades[cat] = round(sum(scores) / len(scores), 2) if scores else 0.50

    return {
        "direction": direction,
        "confidence": confidence,
        "strength": strength,
        "regime": regime,
        "grades": grades,
    }


# --------------------- LOSS AND PROFIT STOPS --------------------- #


def get_loss_and_profit_stops(market: str, direction: str):
    """
    This function serves to get the stop_loss and take_profit of a determinited market.
    Based on the strength and confidence of the market movement.
    Determining the market based on previous smr.
    """

    candles = cache.cached_p42(market)
    actual_value = candles[-1][4]
    stop_losses_events = indicators.smr(candles=candles)

    last_high_val = None
    last_low_val = None

    # 1. Iterate to find the MOST RECENT structural points
    for a in stop_losses_events:
        i = a["index"]
        idx = max(0, i - 2)

        if a["type"] in ("HH", "LH"):
            last_high_val = candles[idx][2]
        elif a["type"] in ("HL", "LL"):
            last_low_val = candles[idx][3]

    # 2. Assign SL based on direction
    if direction == "buy":
        stop_loss = last_low_val if last_low_val else actual_value * 0.98

        if stop_loss >= actual_value:
            stop_loss = actual_value * 0.99

        risk_amt = actual_value - stop_loss
        take_profit = actual_value + (risk_amt * r.risk_reward_ratio)

    else:
        stop_loss = last_high_val if last_high_val else actual_value * 1.02

        if stop_loss <= actual_value:
            stop_loss = actual_value * 1.01

        risk_amt = stop_loss - actual_value
        take_profit = actual_value - (risk_amt * r.risk_reward_ratio)

    return stop_loss, take_profit, actual_value


# --------------------- ICEBERG HELPER --------------------- #


def is_iceberg(symbol: str, maximum_share: float, amount: float, price: float):
    candles = np.asarray(cached_p14(symbol), dtype=float)

    if len(candles) < 14:
        logger.error(f"Not enough candles to check iceberg: {len(candles)}")
        return False, amount

    # Take only the last 14 volume entries and average them
    avg_vol = np.mean(candles[-14:, 5])

    if avg_vol == 0:
        logger.error("Not enough volume to check iceberg.")
        return False, amount

    # Thresholds
    upper_threshold = maximum_share * avg_vol
    lower_threshold = 0.01 * avg_vol
    value = amount * price

    # Check against the larger requirement first
    if amount >= upper_threshold and value == 5000:
        return True, upper_threshold

    if amount >= lower_threshold and value == 5000:
        return True, amount

    return False, amount
