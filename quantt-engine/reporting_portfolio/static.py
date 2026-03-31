from datetime import datetime, timezone

from sqlalchemy.orm import Session

from persistance.models import GeneralOrder, TakeStopOrder

# ================================================================== #
#  Helpers                                                             #
# ================================================================== #


def _ts_to_dt(ts_ms: int) -> datetime:
    """Convert a millisecond Unix timestamp to a UTC datetime."""
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)


def get_closed_trades(session: Session) -> list[dict]:
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

    trades = []
    for entry in entrances:
        exit_order = exits_by_time.get(entry.time)
        if not exit_order:
            continue  # still open

        entry_dt = _ts_to_dt(entry.time)
        exit_dt = _ts_to_dt(exit_order.time)
        fees = 0.0

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

    return trades


# ================================================================== #
#  Static metrics — single values / summary cards                     #
# ================================================================== #


def get_max_drawdown(session: Session) -> dict:
    """
    Largest peak-to-trough drop in cumulative P&L.
    Returns absolute value and percentage of the peak.
    """
    trades = get_closed_trades(session)
    if not trades:
        return {"max_drawdown_abs": 0.0, "max_drawdown_pct": 0.0}

    trades.sort(key=lambda t: t["exit_time"])
    cumulative, peak, max_dd = 0.0, 0.0, 0.0

    for t in trades:
        cumulative += t["pnl"]
        if cumulative > peak:
            peak = cumulative
        dd = peak - cumulative
        if dd > max_dd:
            max_dd = dd

    max_dd_pct = (max_dd / peak * 100) if peak > 0 else 0.0
    return {
        "max_drawdown_abs": round(max_dd, 4),
        "max_drawdown_pct": round(max_dd_pct, 2),
    }


def get_sharpe_ratio(session: Session, risk_free_rate: float = 0.0) -> dict:
    """
    Annualised Sharpe ratio based on per-trade P&L.
    Assumes ~252 trading days/year. Returns None if insufficient data.
    """
    trades = get_closed_trades(session)
    if len(trades) < 2:
        return {"sharpe_ratio": None}

    pnls = [t["pnl"] for t in trades]
    n = len(pnls)
    mean = sum(pnls) / n
    std = (sum((p - mean) ** 2 for p in pnls) / (n - 1)) ** 0.5

    if std == 0:
        return {"sharpe_ratio": None}

    sharpe = ((mean - risk_free_rate) / std) * (252**0.5)
    return {"sharpe_ratio": round(sharpe, 4)}


def get_win_rate(session: Session) -> dict:
    """Win rate, average win, average loss, and profit factor."""
    trades = get_closed_trades(session)
    if not trades:
        return {
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_factor": None,
            "total_trades": 0,
        }

    wins = [t["pnl"] for t in trades if t["pnl"] > 0]
    losses = [t["pnl"] for t in trades if t["pnl"] <= 0]

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = round(gross_profit / gross_loss, 4) if gross_loss > 0 else None

    return {
        "win_rate": round(len(wins) / len(trades), 4),
        "avg_win": round(sum(wins) / len(wins), 4) if wins else 0.0,
        "avg_loss": round(sum(losses) / len(losses), 4) if losses else 0.0,
        "profit_factor": profit_factor,
        "total_trades": len(trades),
    }


def get_avg_hold_time(session: Session) -> dict:
    """Average trade hold time in seconds, minutes, and hours."""
    trades = get_closed_trades(session)
    if not trades:
        return {"avg_hold_seconds": 0.0, "avg_hold_minutes": 0.0, "avg_hold_hours": 0.0}

    avg_sec = sum(t["hold_time_sec"] for t in trades) / len(trades)
    return {
        "avg_hold_seconds": round(avg_sec, 2),
        "avg_hold_minutes": round(avg_sec / 60, 2),
        "avg_hold_hours": round(avg_sec / 3600, 2),
    }


def get_best_and_worst_trades(session: Session, n: int = 5) -> dict:
    """Top N and bottom N trades by P&L."""
    trades = get_closed_trades(session)
    if not trades:
        return {"best": [], "worst": []}

    sorted_trades = sorted(trades, key=lambda t: t["pnl"], reverse=True)

    def _fmt(t: dict) -> dict:
        return {
            "symbol": t["symbol"],
            "pnl": round(t["pnl"], 4),
            "entry_time": t["entry_time"].isoformat(),
            "exit_time": t["exit_time"].isoformat(),
            "side": t["side"],
        }

    return {
        "best": [_fmt(t) for t in sorted_trades[:n]],
        "worst": [_fmt(t) for t in sorted_trades[-n:]],
    }


def get_consecutive_wins_losses(session: Session) -> dict:
    """Longest consecutive win and loss streaks."""
    trades = get_closed_trades(session)
    if not trades:
        return {"max_consecutive_wins": 0, "max_consecutive_losses": 0}

    trades.sort(key=lambda t: t["exit_time"])
    max_wins = max_losses = cur_wins = cur_losses = 0

    for t in trades:
        if t["pnl"] > 0:
            cur_wins += 1
            cur_losses = 0
        else:
            cur_losses += 1
            cur_wins = 0
        max_wins = max(max_wins, cur_wins)
        max_losses = max(max_losses, cur_losses)

    return {"max_consecutive_wins": max_wins, "max_consecutive_losses": max_losses}
