import React, { useState, useEffect, useCallback, useRef } from "react";
import api from "../../../api/axiosInstance.js";
import "../localassets/Graphs.css";

import EquityCurveChart from "../../components/charts/EquityCurve";
import DailyPnlChart from "../../components/charts/DailyPnl";
import DrawdownChart from "../../components/charts/Drawdown";
import DailyTradeCountChart from "../../components/charts/DailyTradeCount";

// ─── Types ────────────────────────────────────────────────────────────────────

interface EquityPoint {
  timestamp: string;
  equity: number;
}

interface DailyPnlPoint {
  date: string;
  pnl: number;
}

interface DrawdownPoint {
  timestamp: string;
  drawdown_abs: number;
  drawdown_pct: number;
}

interface TradeCountPoint {
  date: string;
  count: number;
}

interface TradeRow {
  id: string | number;
  entry_time: string;
  exit_time: string;
  [key: string]: any;
}

interface TradesPage {
  trades: TradeRow[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

interface GraphState<T> {
  data: T[];
  loading: boolean;
  error: string | null;
}

// ─── Constants ────────────────────────────────────────────────────────────────

const POLL_INTERVAL_MS = 5000;

// ─── Small helpers ────────────────────────────────────────────────────────────

function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span
      className={`status-indicator ${ok ? "blue-bg" : ""}`}
      style={!ok ? { backgroundColor: "#555", boxShadow: "none" } : undefined}
    />
  );
}

function GraphCard({
  title,
  accentClass,
  loading,
  error,
  children,
}: {
  title: string;
  accentClass: "blue" | "purple" | "red" | "green";
  loading: boolean;
  error: string | null;
  children: React.ReactNode;
}) {
  const colorMap = {
    blue: "#2563eb",
    purple: "#8a5cf6",
    red: "#ef4444",
    green: "#22c55e",
  };

  return (
    <div className="graph-item-card">
      <div className="graph-item-header">
        <span
          className="status-indicator"
          style={{
            backgroundColor: colorMap[accentClass],
            boxShadow: `0 0 8px ${colorMap[accentClass]}`,
          }}
        />
        <h4>{title}</h4>
        <span
          className="trade-time"
          style={{ display: "flex", alignItems: "center", gap: 6 }}
        >
          {loading && (
            <span
              className="status-indicator pulse highlight-silver-bg"
              style={{ width: 6, height: 6 }}
            />
          )}
          {loading ? "Syncing…" : error ? "Error" : "Live"}
        </span>
      </div>

      <div className="graph-content-area" style={{ padding: "8px 4px 4px" }}>
        {error ? (
          <p
            style={{
              color: "#ef4444",
              fontFamily: "DM Mono, monospace",
              fontSize: 11,
            }}
          >
            {error}
          </p>
        ) : loading && !React.Children.count(children) ? (
          <p
            className="silver-text"
            style={{ fontFamily: "DM Mono, monospace", fontSize: 11 }}
          >
            Loading…
          </p>
        ) : (
          children
        )}
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function Graphs() {
  // Per-endpoint state
  const [equity, setEquity] = useState<GraphState<EquityPoint>>({
    data: [],
    loading: true,
    error: null,
  });
  const [pnl, setPnl] = useState<GraphState<DailyPnlPoint>>({
    data: [],
    loading: true,
    error: null,
  });
  const [drawdown, setDrawdown] = useState<GraphState<DrawdownPoint>>({
    data: [],
    loading: true,
    error: null,
  });
  const [tradeCount, setTradeCount] = useState<GraphState<TradeCountPoint>>({
    data: [],
    loading: true,
    error: null,
  });
  const [tradesPage, setTradesPage] = useState<TradesPage | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  // Track whether a fetch is in-flight so polling doesn't stack
  const fetchingRef = useRef(false);

  // ── Fetchers ────────────────────────────────────────────────────────────────

  const fetchEquity = useCallback(async () => {
    try {
      const { data } = await api.get<EquityPoint[]>("/report/equity-curve");
      setEquity({ data, loading: false, error: null });
    } catch (e: any) {
      setEquity((prev) => ({
        ...prev,
        loading: false,
        error: e?.message ?? "Failed",
      }));
    }
  }, []);

  const fetchPnl = useCallback(async () => {
    try {
      const { data } = await api.get<DailyPnlPoint[]>("/report/daily-pnl");
      setPnl({ data, loading: false, error: null });
    } catch (e: any) {
      setPnl((prev) => ({
        ...prev,
        loading: false,
        error: e?.message ?? "Failed",
      }));
    }
  }, []);

  const fetchDrawdown = useCallback(async () => {
    try {
      const { data } = await api.get<DrawdownPoint[]>("/report/drawdown");
      setDrawdown({ data, loading: false, error: null });
    } catch (e: any) {
      setDrawdown((prev) => ({
        ...prev,
        loading: false,
        error: e?.message ?? "Failed",
      }));
    }
  }, []);

  const fetchTradeCount = useCallback(async () => {
    try {
      const { data } = await api.get<TradeCountPoint[]>(
        "/report/daily-trade-count",
      );
      setTradeCount({ data, loading: false, error: null });
    } catch (e: any) {
      setTradeCount((prev) => ({
        ...prev,
        loading: false,
        error: e?.message ?? "Failed",
      }));
    }
  }, []);

  const fetchTrades = useCallback(async (page: number) => {
    try {
      const { data } = await api.get<TradesPage>("/report/trades", {
        params: { page, page_size: 10 },
      });
      setTradesPage(data);
    } catch {
      // Non-critical — trades table is supplementary
    }
  }, []);

  // ── Polling ──────────────────────────────────────────────────────────────────

  const pollAll = useCallback(async () => {
    if (fetchingRef.current) return;
    fetchingRef.current = true;
    await Promise.allSettled([
      fetchEquity(),
      fetchPnl(),
      fetchDrawdown(),
      fetchTradeCount(),
    ]);
    fetchingRef.current = false;
  }, [fetchEquity, fetchPnl, fetchDrawdown, fetchTradeCount]);

  useEffect(() => {
    pollAll();
    fetchTrades(currentPage);

    const interval = setInterval(pollAll, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [pollAll, fetchTrades, currentPage]);

  // Re-fetch trades whenever page changes
  useEffect(() => {
    fetchTrades(currentPage);
  }, [currentPage, fetchTrades]);

  // ── Derived metrics for top cards ───────────────────────────────────────────

  const lastEquity = equity.data[equity.data.length - 1]?.equity ?? null;
  const totalPnl = pnl.data.reduce((sum, d) => sum + d.pnl, 0);
  const maxDrawdown = drawdown.data.reduce(
    (max, d) => (d.drawdown_pct > max ? d.drawdown_pct : max),
    0,
  );

  // ─────────────────────────────────────────────────────────────────────────────

  return (
    <div className="home-container">
      {/* Header */}
      <div className="section-header">
        <h2 className="section-title">Visual Analytics</h2>
        <div className="activity-count">
          Polling · {POLL_INTERVAL_MS / 1000}s
        </div>
      </div>

      {/* Top Metrics Grid */}
      <div className="metrics-grid">
        <div className="metric-card highlight-blue">
          <div className="metric-header">
            <span className="metric-label">Portfolio Equity</span>
          </div>
          <div className="metric-value">
            <span>{lastEquity !== null ? lastEquity.toFixed(4) : "—"}</span>
          </div>
          {/* Mini sparkline */}
          <div style={{ height: 60, marginTop: 12 }}>
            {equity.data.length > 0 && (
              <EquityCurveChart data={equity.data.slice(-30)} />
            )}
          </div>
        </div>

        <div className="metric-card highlight-purple">
          <div className="metric-header">
            <span className="metric-label">Cumulative PnL</span>
          </div>
          <div className={`metric-value ${totalPnl >= 0 ? "positive" : ""}`}>
            <span>
              {totalPnl >= 0 ? "+" : ""}
              {totalPnl.toFixed(4)}
            </span>
          </div>
          <div style={{ height: 60, marginTop: 12 }}>
            {pnl.data.length > 0 && (
              <DailyPnlChart data={pnl.data.slice(-30)} />
            )}
          </div>
        </div>
      </div>

      {/* Scrollable Graph Feed */}
      <div className="graph-feed-container">
        <h3 className="sub-section-title">
          Historical Trends &amp; Indicators
        </h3>

        <div className="infinite-graph-list">
          {/* 1 — Equity Curve */}
          <GraphCard
            title="Equity Curve"
            accentClass="blue"
            loading={equity.loading}
            error={equity.error}
          >
            <EquityCurveChart data={equity.data} />
          </GraphCard>

          {/* 2 — Daily PnL */}
          <GraphCard
            title="Daily PnL"
            accentClass="green"
            loading={pnl.loading}
            error={pnl.error}
          >
            <DailyPnlChart data={pnl.data} />
          </GraphCard>

          {/* 3 — Drawdown */}
          <GraphCard
            title="Drawdown (Abs &amp; %)"
            accentClass="red"
            loading={drawdown.loading}
            error={drawdown.error}
          >
            <DrawdownChart data={drawdown.data} />
          </GraphCard>

          {/* 4 — Daily Trade Count */}
          <GraphCard
            title="Daily Trade Count"
            accentClass="purple"
            loading={tradeCount.loading}
            error={tradeCount.error}
          >
            <DailyTradeCountChart data={tradeCount.data} />
          </GraphCard>

          {/* 5 — Trades Table */}
          {tradesPage && (
            <div className="graph-item-card">
              <div className="graph-item-header">
                <span className="status-indicator blue-bg" />
                <h4>Recent Trades</h4>
                <span className="trade-time silver-text">
                  {tradesPage.total} total · page {tradesPage.page}/
                  {tradesPage.pages}
                </span>
              </div>

              <div
                style={{
                  overflowX: "auto",
                  fontFamily: "DM Mono, monospace",
                  fontSize: 11,
                }}
              >
                <table
                  style={{
                    width: "100%",
                    borderCollapse: "collapse",
                    color: "#c0c0c0",
                  }}
                >
                  <thead>
                    <tr style={{ borderBottom: "1px solid #2a2a2a" }}>
                      {tradesPage.trades[0] &&
                        Object.keys(tradesPage.trades[0]).map((col) => (
                          <th
                            key={col}
                            style={{
                              textAlign: "left",
                              padding: "6px 10px",
                              color: "#555",
                              fontWeight: 400,
                              whiteSpace: "nowrap",
                              textTransform: "uppercase",
                              letterSpacing: "0.08em",
                              fontSize: 9,
                            }}
                          >
                            {col}
                          </th>
                        ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tradesPage.trades.map((trade, i) => (
                      <tr
                        key={trade.id ?? i}
                        style={{
                          borderBottom: "1px solid #1a1a1a",
                          transition: "background 0.15s",
                        }}
                        onMouseEnter={(e) =>
                          (e.currentTarget.style.background = "#161616")
                        }
                        onMouseLeave={(e) =>
                          (e.currentTarget.style.background = "transparent")
                        }
                      >
                        {Object.values(trade).map((val, j) => (
                          <td
                            key={j}
                            style={{
                              padding: "6px 10px",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {String(val)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="graph-item-footer" style={{ marginTop: 12 }}>
                <button
                  className="control-btn restart-btn"
                  disabled={currentPage <= 1}
                  onClick={() => setCurrentPage((p) => p - 1)}
                >
                  ← Prev
                </button>
                <button
                  className="control-btn start-btn"
                  disabled={currentPage >= tradesPage.pages}
                  onClick={() => setCurrentPage((p) => p + 1)}
                >
                  Next →
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="loading-trigger">
          <span className="status-indicator pulse highlight-silver-bg" />
          <p>Polling · next refresh in {POLL_INTERVAL_MS / 1000}s</p>
        </div>
      </div>

      {/* Control Bar */}
      <div className="control-bar">
        <div className="control-status">
          <StatusDot
            ok={
              !equity.error &&
              !pnl.error &&
              !drawdown.error &&
              !tradeCount.error
            }
          />
          <span className="status-text">
            Engine:{" "}
            <strong>
              {equity.error || pnl.error || drawdown.error || tradeCount.error
                ? "Partial Error"
                : "All Feeds Live"}
            </strong>
          </span>
          {maxDrawdown > 0 && (
            <span style={{ marginLeft: 16, color: "#ef4444", fontSize: 11 }}>
              Max DD {maxDrawdown.toFixed(2)}%
            </span>
          )}
        </div>
        <div className="control-actions">
          <button
            className="control-btn stop-btn"
            onClick={() => {
              setEquity({ data: [], loading: true, error: null });
              setPnl({ data: [], loading: true, error: null });
              setDrawdown({ data: [], loading: true, error: null });
              setTradeCount({ data: [], loading: true, error: null });
              setTradesPage(null);
              setCurrentPage(1);
              pollAll();
              fetchTrades(1);
            }}
          >
            Refresh All
          </button>
        </div>
      </div>
    </div>
  );
}
