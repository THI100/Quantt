from typing import Optional

from fastapi import APIRouter, HTTPException

from core.bot import TradingBot
from persistance.connection import SessionLocal
from reporting_portfolio.roll import (
    get_closed_trades,
    get_daily_pnl,
    get_daily_trade_count,
    get_drawdown_series,
    get_equity_curve,
)
from reporting_portfolio.static import (
    get_avg_hold_time,
    get_best_and_worst_trades,
    get_consecutive_wins_losses,
    get_max_drawdown,
    get_sharpe_ratio,
    get_win_rate,
)

r_route = APIRouter()
bot = TradingBot()

# ------------------------------------------------------------------ #
#  Helper                                                              #
# ------------------------------------------------------------------ #


def _require_running():
    """Raise 400 if the bot is not active."""
    if not bot.is_running:
        raise HTTPException(status_code=400, detail="Bot is not running.")


# ------------------------------------------------------------------ #
#  Positions                                                           #
# ------------------------------------------------------------------ #


@r_route.get("/positions/{symbol}")
def get_position(symbol: str, id: str):
    """Return details for a single open position."""
    _require_running()
    position = bot.fet_order(symbol, id)
    if not position:
        raise HTTPException(status_code=404, detail=f"No open position for '{symbol}'.")
    return position


@r_route.delete("/positions/{symbol}")
def close_position(symbol: str, id: str):
    """Force-close a position by symbol, sending a market order."""
    _require_running()
    try:
        bot.close_order(symbol, id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to close position: {str(e)}"
        )
    return {"status": "closed", "symbol": symbol}


# ------------------------------------------------------------------ #
#  Reports                                                             #
# ------------------------------------------------------------------ #

# --- Static endpoints (summary cards) --- #


@r_route.get("/report/summary")
def get_summary():
    """
    All static metrics in one call — intended for dashboard KPI cards.
    Covers win rate, hold time, drawdown, Sharpe, streaks.
    """
    db = SessionLocal()
    try:
        trades = get_closed_trades(db)
        total_pnl = round(sum(t["pnl"] for t in trades), 4)
        avg_pnl = round(total_pnl / len(trades), 4) if trades else 0.0

        return {
            "total_trades": len(trades),
            "total_pnl": total_pnl,
            "avg_pnl": avg_pnl,
            **get_win_rate(db),
            **get_avg_hold_time(db),
            **get_max_drawdown(db),
            **get_sharpe_ratio(db),
            **get_consecutive_wins_losses(db),
            **bot.check_margin()
        }
    finally:
        db.close()


@r_route.get("/report/margin-health")
def get_margin_health():
    """
    Get directly from the bot the margin in usage.
    Important for balance control.
    """
    return bot.check_margin()


@r_route.get("/report/best-worst")
def get_best_worst(n: int = 5):
    """
    Top N and bottom N trades by P&L.
    Query param: ?n=5 (default 5)
    """
    db = SessionLocal()
    try:
        return get_best_and_worst_trades(db, n=n)
    finally:
        db.close()


@r_route.get("/report/win-rate")
def get_win_rate_endpoint():
    """Win rate, avg win, avg loss and profit factor."""
    db = SessionLocal()
    try:
        return get_win_rate(db)
    finally:
        db.close()


@r_route.get("/report/hold-time")
def get_hold_time():
    """Average trade hold time in seconds, minutes and hours."""
    db = SessionLocal()
    try:
        return get_avg_hold_time(db)
    finally:
        db.close()


@r_route.get("/report/max-drawdown")
def get_max_drawdown_endpoint():
    """Single worst peak-to-trough drop, absolute and percentage."""
    db = SessionLocal()
    try:
        return get_max_drawdown(db)
    finally:
        db.close()


@r_route.get("/report/sharpe")
def get_sharpe(risk_free_rate: float = 0.0):
    """
    Annualised Sharpe ratio.
    Query param: ?risk_free_rate=0.0 (default 0.0)
    """
    db = SessionLocal()
    try:
        return get_sharpe_ratio(db, risk_free_rate=risk_free_rate)
    finally:
        db.close()


@r_route.get("/report/streaks")
def get_streaks():
    """Longest consecutive win and loss streaks."""
    db = SessionLocal()
    try:
        return get_consecutive_wins_losses(db)
    finally:
        db.close()


# --- Series endpoints (chart data) --- #


@r_route.get("/report/trades")
def get_trades(
    page: int = 1,
    page_size: int = 50,
    symbol: Optional[str] = None,
):
    """
    Paginated list of closed trades.
    Query params: ?page=1&page_size=50&symbol=BTCUSDT
    """
    db = SessionLocal()
    try:
        trades = get_closed_trades(db)

        if symbol:
            trades = [t for t in trades if t["symbol"].upper() == symbol.upper()]

        trades.sort(key=lambda t: t["exit_time"], reverse=True)

        total = len(trades)
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "trades": [
                {
                    **t,
                    "entry_time": t["entry_time"].isoformat(),
                    "exit_time": t["exit_time"].isoformat(),
                }
                for t in trades[start:end]
            ],
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": -(-total // page_size),  # ceiling division
        }
    finally:
        db.close()


@r_route.get("/report/equity-curve")
def get_equity_curve_endpoint():
    """
    Cumulative P&L over time.
    Returns: [ { timestamp, equity } ]
    Frontend: Line chart.
    """
    db = SessionLocal()
    try:
        return get_equity_curve(db)
    finally:
        db.close()


@r_route.get("/report/daily-pnl")
def get_daily_pnl_endpoint():
    """
    P&L grouped by UTC calendar day.
    Returns: [ { date, pnl } ]
    Frontend: Green/red bar chart.
    """
    db = SessionLocal()
    try:
        return get_daily_pnl(db)
    finally:
        db.close()


@r_route.get("/report/drawdown")
def get_drawdown():
    """
    Drawdown at each closed trade exit.
    Returns: [ { timestamp, drawdown_abs, drawdown_pct } ]
    Frontend: Red filled area chart.
    """
    db = SessionLocal()
    try:
        return get_drawdown_series(db)
    finally:
        db.close()


@r_route.get("/report/daily-trade-count")
def get_daily_trade_count_endpoint():
    """
    Number of trades closed per UTC calendar day.
    Returns: [ { date, count } ]
    Frontend: Bar chart.
    """
    db = SessionLocal()
    try:
        return get_daily_trade_count(db)
    finally:
        db.close()
