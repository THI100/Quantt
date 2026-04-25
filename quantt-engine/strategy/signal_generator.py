import strategy.indicators as indicators
from config import risk
from data import cache
from utils.math import scale_0_100

r = risk.RiskConfig()

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
        "bos_bullish": 1.5, "bos_bearish": 1.5,
        "choch_bullish": 2.0, "choch_bearish": 2.0,
        "fvg_bullish": 0.7, "fvg_bearish": 0.7
    }

    for e in smr_events:
        etype = e["type"]
        if etype not in WEIGHTS:
            continue

        weight = WEIGHTS[etype]
        # Decay factor: makes older SMR events less relevant than fresh breakouts
        recency_weight = e["index"] / total_len if total_len > 0 else 1.0
        impact = abs(e["multiplicator"]) * min(e["volume_strength"], 2.0) * weight * recency_weight

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

    # Track raw normalized scores (0.0 to 1.0) for each category
    category_scores = {
        "trend": [],
        "momentum": [],
        "volume": [],
        "structure": []
    }

    # Regime and Strength specific trackers
    adx_val = 20.0 # Default fallback
    atr_ratio = 0.5

    # 3. Process each indicator if present in parameters
    parameters_lower = [p.lower() for p in parameters]

    if "vwap" in parameters_lower:
        vwap_value, vwap_mean, vwap_series = indicators.vwap(candles)
        score = 1.0 if vwap_value > vwap_mean else 0.0
        category_scores["trend"].append(score)
        if score > 0.5: bull_votes += 1
        else: bear_votes += 1
        total_signals += 1

    if "rsi" in parameters_lower:
        rsi_value, rsi_mean, rsi_series = indicators.rsi(candles)
        score = rsi_value / 100.0 # Normalize 0-100 to 0.0-1.0
        category_scores["momentum"].append(score)
        if rsi_value > 50: bull_votes += 1
        else: bear_votes += 1
        total_signals += 1

    if "tnk" in parameters_lower:
        tenkan_sen, kijun_sen = indicators.tenkan_and_kijun(candles)
        score = 1.0 if tenkan_sen > kijun_sen else 0.0
        category_scores["trend"].append(score)
        if score > 0.5: bull_votes += 1
        else: bear_votes += 1
        total_signals += 1

    if "macd" in parameters_lower:
        macd_value, signal_value, hist_value, macd_series, signal_series, hist_series = indicators.macd(candles)
        score = 1.0 if hist_value > 0 else 0.0
        category_scores["momentum"].append(score)
        if hist_value > 0: bull_votes += 1
        else: bear_votes += 1
        total_signals += 1

    if "ema" in parameters_lower:
        ema_value, ema_mean, ema_series = indicators.ema(candles)
        score = 1.0 if ema_value > ema_mean else 0.0
        category_scores["trend"].append(score)
        if score > 0.5: bull_votes += 1
        else: bear_votes += 1
        total_signals += 1

    if "atr" in parameters_lower:
        atr_value, atr_mean, atr_series = indicators.atr(candles)
        atr_ratio = min(atr_value / (atr_mean + 1e-9), 1.0) # Avoid div by zero
        category_scores["structure"].append(atr_ratio) # High ATR = high volatility structure

    if "roc" in parameters_lower:
        roc_value, roc_mean, roc_series = indicators.roc(candles)
        score = 1.0 if roc_value > 0 else 0.0
        category_scores["momentum"].append(score)
        if roc_value > 0: bull_votes += 1
        else: bear_votes += 1
        total_signals += 1

    if "st" in parameters_lower:
        last_st, last_dir, st_series = indicators.supertrend(candles)
        score = 1.0 if last_dir == "up" else 0.0
        category_scores["trend"].append(score)
        if last_dir == "up": bull_votes += 1
        else: bear_votes += 1
        total_signals += 1

    if "bb" in parameters_lower:
        last_bands, bb_mean_width, bb_series = indicators.bollinger_bands(candles)
        upper, middle, lower = last_bands
        # Position of price relative to bands (estimating price is near middle for safe proxy)
        # Using bandwidth squeeze as a structure metric
        bb_width = upper - lower
        squeeze_ratio = min(bb_width / (bb_mean_width + 1e-9), 1.0)
        category_scores["structure"].append(squeeze_ratio)

    if "adx" in parameters_lower:
        adx_value, adx_mean, adx_series = indicators.adx(candles)
        adx_val = adx_value
        score = min(adx_value / 50.0, 1.0) # ADX > 25 is strong trend, cap at 50 for max score
        category_scores["trend"].append(score)

    if "obv" in parameters_lower:
        obv_value, obv_mean, obv_series = indicators.obv(candles)
        score = 1.0 if obv_value > obv_mean else 0.0
        category_scores["volume"].append(score)
        if obv_value > obv_mean: bull_votes += 1
        else: bear_votes += 1
        total_signals += 1

    # Note: These two functions take 'Market' directly, not 'candles'
    if "dscp" in parameters_lower:
        m_force_bull, m_force_bear, conf_bull, conf_bear = get_signal_candlestick_patterns(Market)
        if m_force_bull > m_force_bear:
            bull_votes += 1
            category_scores["structure"].append(min(m_force_bull + conf_bull, 1.0))
        elif m_force_bear > m_force_bull:
            bear_votes += 1
            category_scores["structure"].append(max(0.0, 1.0 - (m_force_bear + conf_bear)))
        total_signals += 1

    if "smr" in parameters_lower:
        m_force_bull, m_force_bear, conf_bull, conf_bear = get_signal_smr(Market)
        if m_force_bull > m_force_bear:
            bull_votes += 1
            category_scores["structure"].append(min(m_force_bull + conf_bull, 1.0))
        elif m_force_bear > m_force_bull:
            bear_votes += 1
            category_scores["structure"].append(max(0.0, 1.0 - (m_force_bear + conf_bear)))
        total_signals += 1

    # 4. Aggregate results
    # Determine Direction & Confidence
    direction = "NEUTRAL"
    confidence = 0.50

    if total_signals > 0:
        if bull_votes > bear_votes:
            direction = "BUY"
            confidence = round(bull_votes / total_signals, 2)
        elif bear_votes > bull_votes:
            direction = "SELL"
            confidence = round(bear_votes / total_signals, 2)
        else:
            direction = "NEUTRAL"
            confidence = 0.50

    # Determine Strength and Regime
    # ADX > 25 is typically the threshold for a trending market
    regime = "TREND" if adx_val >= 25.0 else "RANGE"

    # Calculate overall strength (using ADX normalized as primary, fallback to ATR ratio)
    strength = round(min(adx_val / 50.0, 1.0), 2) if "adx" in parameters_lower else round(atr_ratio, 2)

    # Calculate average grades per category (fallback to 0.5 if category had no indicators triggered)
    grades = {}
    for cat, scores in category_scores.items():
        if scores:
            grades[cat] = round(sum(scores) / len(scores), 2)
        else:
            grades[cat] = 0.50 # Default neutral grade if not evaluated

    # 5. Return final dictionary
    return {
        "direction": direction,
        "confidence": confidence,
        "strength": strength,
        "regime": regime,
        "grades": grades
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
        # Ensure we don't hit an IndexError
        idx = max(0, i - 2)

        if a["type"] in ("HH", "LH"):
            last_high_val = candles[idx][2]
        elif a["type"] in ("HL", "LL"):
            last_low_val = candles[idx][3]

    # 2. Assign SL based on direction
    if direction == "bullish":
        # For bullish, SL should be the last structural LOW
        stop_loss = last_low_val if last_low_val else actual_value * 0.98

        # Emergency check: SL must be below price
        if stop_loss >= actual_value:
            stop_loss = actual_value * 0.99

        risk_amt = actual_value - stop_loss
        take_profit = actual_value + (risk_amt * r.risk_reward_ratio)

    else:  # bearish
        # For bearish, SL should be the last structural HIGH
        stop_loss = last_high_val if last_high_val else actual_value * 1.02

        # Emergency check: SL must be above price
        if stop_loss <= actual_value:
            stop_loss = actual_value * 1.01

        risk_amt = stop_loss - actual_value
        take_profit = actual_value - (risk_amt * r.risk_reward_ratio)

    return stop_loss, take_profit, actual_value
