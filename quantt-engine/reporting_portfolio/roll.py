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
#  Series / graphic data — lists of {x, y} points for charts         #
# ================================================================== #


def get_equity_curve(session: Session) -> list[dict]:
    """
    Cumulative P&L over time.
    Each point: { timestamp (ISO), equity (float) }
    Frontend: Line chart.
    """
    trades = get_closed_trades(session)
    trades.sort(key=lambda t: t["exit_time"])

    cumulative = 0.0
    curve = []
    for t in trades:
        cumulative += t["pnl"]
        curve.append(
            {
                "timestamp": t["exit_time"].isoformat(),
                "equity": round(cumulative, 4),
            }
        )
    return curve


def get_daily_pnl(session: Session) -> list[dict]:
    """
    P&L grouped by UTC calendar day.
    Each point: { date (YYYY-MM-DD), pnl (float) }
    Frontend: Green/red bar chart.
    """
    trades = get_closed_trades(session)
    daily: dict[str, float] = {}

    for t in trades:
        day = t["exit_time"].strftime("%Y-%m-%d")
        daily[day] = daily.get(day, 0.0) + t["pnl"]

    return [{"date": day, "pnl": round(pnl, 4)} for day, pnl in sorted(daily.items())]


def get_drawdown_series(session: Session) -> list[dict]:
    """
    Drawdown at each closed trade exit — how far below the running peak.
    Each point: { timestamp (ISO), drawdown_abs (float), drawdown_pct (float) }
    Frontend: Red filled area chart.
    """
    trades = get_closed_trades(session)
    trades.sort(key=lambda t: t["exit_time"])

    cumulative = peak = 0.0
    series = []

    for t in trades:
        cumulative += t["pnl"]
        if cumulative > peak:
            peak = cumulative
        dd_abs = peak - cumulative
        dd_pct = (dd_abs / peak * 100) if peak > 0 else 0.0
        series.append(
            {
                "timestamp": t["exit_time"].isoformat(),
                "drawdown_abs": round(dd_abs, 4),
                "drawdown_pct": round(dd_pct, 2),
            }
        )
    return series


def get_daily_trade_count(session: Session) -> list[dict]:
    """
    Number of trades closed per UTC calendar day.
    Each point: { date (YYYY-MM-DD), count (int) }
    Frontend: Bar chart.
    """
    trades = get_closed_trades(session)
    daily: dict[str, int] = {}

    for t in trades:
        day = t["exit_time"].strftime("%Y-%m-%d")
        daily[day] = daily.get(day, 0) + 1

    return [{"date": day, "count": count} for day, count in sorted(daily.items())]
