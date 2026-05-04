import math
import time
from datetime import datetime, timezone

from loguru import logger
from sqlalchemy.orm import Session

from config import store
from data import fetch
from persistance.models import GeneralOrder, TakeStopOrder

# ================================================================== #
#  Initializations                                                   #
# ================================================================== #

store_cfg = store.watcher.get_config()

# ================================================================== #
#  Helpers                                                           #
# ================================================================== #


def _safe_float(value, field_name="value") -> float:
    """Helper to validate that a value is a finite number."""
    try:
        if value is None:
            raise ValueError(f"{field_name} is None")

        f_val = float(value)
        if math.isnan(f_val) or math.isinf(f_val):
            raise ValueError(f"{field_name} is NaN or Inf")

        return f_val
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid numeric data detected: {e}. Defaulting to 0.0")
        return 0.0


def _ts_to_dt(ts_ms: int) -> datetime:
    """Convert a millisecond Unix timestamp to a UTC datetime."""
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)


def get_closed_trades(session: Session) -> tuple[float, list[dict]]:
    """
    Core helper — pairs every 'entrance' order with its matching 'exit' order
    by symbol and previous_time, then returns a clean list of trade dicts.
    All reporting functions build on top of this.
    """
    entrances = (
        session.query(GeneralOrder)
        .filter(GeneralOrder.entrance_exit == "entrance")
        .all()
    )
    exits_by_time = {
        o.previous_time: o
        for o in session.query(GeneralOrder)
        .filter(GeneralOrder.entrance_exit == "exit")
        .all()
    }

    # Alive PnL, No need for trades
    store_t = store_cfg.balances.get("USDT", 0.0)
    time.sleep(1)
    actual = fetch.balance()
    actual_t = actual.get("USDT", {}).get("total", 0.0)
    alive_pnl = actual_t - store_t

    trades = []
    for entry in entrances:
        exit_order = exits_by_time.get(entry.time)
        if not exit_order:
            continue  # still open

        entry_dt = _ts_to_dt(int(entry.time))
        exit_dt = _ts_to_dt(int(exit_order.time))
        fees = 0.0

        # Fees, some exchanges doesnt share this
        if exit_order.take_id:
            take = session.get(TakeStopOrder, exit_order.take_id)
            if take:
                fees += take.fees
        if exit_order.stop_id:
            stop = session.get(TakeStopOrder, exit_order.stop_id)
            if stop:
                fees += stop.fees

        pnl = ((exit_order.price - entry.price) * entry.amount) - fees
        if entry.side.lower() == "sell":
            pnl = -pnl

        trades.append(
            {
                "symbol": entry.symbol,
                "side": entry.side,
                "entry_price": entry.price,
                "exit_price": exit_order.price,
                "amount": entry.amount,
                "pnl": pnl,
                "fees": fees,
                "entry_time": entry_dt,
                "exit_time": exit_dt,
                "hold_time_sec": (exit_dt - entry_dt).total_seconds(),
            }
        )

    return alive_pnl, trades


# ================================================================== #
#  Static metrics — single values / summary cards                     #
#  All metrics use snapshot-based `untracked_pnl`.                    #
# ================================================================== #


def get_max_drawdown(session: Session) -> dict:
    alive_pnl, trades = get_closed_trades(session)
    if not trades:
        return {"max_drawdown_abs": 0.0, "max_drawdown_pct": 0.0}

    # Ensure alive_pnl is valid
    alive_pnl = _safe_float(alive_pnl, "alive_pnl")

    trades.sort(key=lambda t: t["exit_time"])
    cumulative, peak, max_dd = alive_pnl, 0.0, 0.0

    if cumulative > peak:
        peak = cumulative
    dd = peak - cumulative
    if dd > max_dd:
        max_dd = dd

    # If you want by trade info and pnl, it wont be live and might have some accuracy issues.
    # for t in trades:
    #     pnl = _safe_float(t.get("pnl"), "trade_pnl")
    #     cumulative += pnl
    #     if cumulative > peak:
    #         peak = cumulative
    #     dd = peak - cumulative
    #     if dd > max_dd:
    #         max_dd = dd

    max_dd_pct = (max_dd / peak * 100) if peak > 0 else 0.0
    return {
        "max_drawdown_abs": round(max_dd, 4),
        "max_drawdown_pct": round(_safe_float(max_dd_pct), 2),
    }


def get_sharpe_ratio(session: Session, risk_free_rate: float = 0.0) -> dict:
    _, trades = get_closed_trades(session)
    if len(trades) < 2:
        return {"sharpe_ratio": 0.0}

    pnls = [_safe_float(t.get("pnl"), "pnl") for t in trades]
    n = len(pnls)
    mean = sum(pnls) / n

    variance = sum((p - mean) ** 2 for p in pnls) / (n - 1)
    std = variance**0.5

    if std <= 0 or math.isnan(std):
        return {"sharpe_ratio": 0.0}

    sharpe = ((mean - risk_free_rate) / std) * (252**0.5)
    return {"sharpe_ratio": round(_safe_float(sharpe), 4)}


def get_win_rate(session: Session) -> dict:
    _, trades = get_closed_trades(session)
    if not trades:
        return {
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": 0.0,
            "total_trades": 0,
        }

    pnls = [_safe_float(t.get("pnl"), "pnl") for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))

    profit_factor = 0.0
    if gross_loss > 0:
        pf_calc = gross_profit / gross_loss
        profit_factor = _safe_float(pf_calc, "profit_factor")

    return {
        "win_rate": round(len(wins) / len(trades), 4),
        "avg_win": round(sum(wins) / len(wins), 4) if wins else 0.0,
        "avg_loss": round(sum(losses) / len(losses), 4) if losses else 0.0,
        "profit_factor": round(profit_factor, 4),
        "total_trades": len(trades),
    }


def get_avg_hold_time(session: Session) -> dict:
    _, trades = get_closed_trades(session)
    if not trades:
        return {"avg_hold_seconds": 0.0, "avg_hold_minutes": 0.0, "avg_hold_hours": 0.0}

    # Validate hold_time_sec for every trade
    times = [_safe_float(t.get("hold_time_sec"), "hold_time_sec") for t in trades]
    avg_sec = sum(times) / len(times)

    return {
        "avg_hold_seconds": round(avg_sec, 2),
        "avg_hold_minutes": round(avg_sec / 60, 2),
        "avg_hold_hours": round(avg_sec / 3600, 2),
    }


def get_best_and_worst_trades(session: Session, n: int = 5) -> dict:
    _, trades = get_closed_trades(session)
    if not trades:
        return {"best": [], "worst": []}

    # Clean PnLs before sorting to avoid Comparison errors with None/NaN
    for t in trades:
        t["pnl"] = _safe_float(t.get("pnl"), "pnl")

    sorted_trades = sorted(trades, key=lambda t: t["pnl"], reverse=True)

    def _fmt(t: dict) -> dict:
        return {
            "symbol": t.get("symbol", "UNKNOWN"),
            "pnl": round(t["pnl"], 4),
            "entry_time": t["entry_time"].isoformat()
            if hasattr(t.get("entry_time"), "isoformat")
            else "N/A",
            "exit_time": t["exit_time"].isoformat()
            if hasattr(t.get("exit_time"), "isoformat")
            else "N/A",
            "side": t.get("side", "UNKNOWN"),
        }

    return {
        "best": [_fmt(t) for t in sorted_trades[:n]],
        "worst": [_fmt(t) for t in sorted_trades[-n:]],
    }


def get_consecutive_wins_losses(session: Session) -> dict:
    _, trades = get_closed_trades(session)
    if not trades:
        return {"max_consecutive_wins": 0, "max_consecutive_losses": 0}

    trades.sort(key=lambda t: t.get("exit_time"))
    max_wins = max_losses = cur_wins = cur_losses = 0

    for t in trades:
        pnl = _safe_float(t.get("pnl"), "pnl")
        if pnl > 0:
            cur_wins += 1
            cur_losses = 0
        else:
            cur_losses += 1
            cur_wins = 0
        max_wins = max(max_wins, cur_wins)
        max_losses = max(max_losses, cur_losses)

    return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}
