import React, { useState, useRef, useEffect } from "react";
import "../localassets/Home.css";
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Shield,
  AlertTriangle,
} from "lucide-react";

import api from "../../../api/axiosInstance.js";
import { getSummary } from "../../../api/services/Info.ts";
import { getPositions } from "../../../api/services/Positions.ts";

interface Trade {
  id: string;
  coin: string;
  type: "BUY" | "SELL";
  price: number;
  profit: number;
  timestamp: Date;
}

interface Metrics {
  pnl: number;
  totalTrades: number;
  marginHealth: number;
  maxDrawdown: number;
}

interface BotResponse {
  status: string;
}

type BotStatus = "Online" | "Offline" | "Restarted" | "Error";

function Home() {
  const [botStatus, setBotStatus] = useState<BotStatus>("Connecting...");
  const [metrics, setMetrics] = useState<Metrics>({
    pnl: 0,
    totalTrades: 0,
    marginHealth: 0,
    maxDrawdown: 0,
  });

  const [recentTrades, setRecentTrades] = useState<Trade[]>([
    {
      id: "0",
      coin: "x",
      type: "x",
      price: 0,
      profit: 0,
      timestamp: new Date(Date.now()),
    },
  ]);

  const hasRun = useRef(false);

  const settingData = async () => {
    try {
      // 1. Fetch raw data
      const summaryRaw = await getSummary();
      const positionsRaw = await getPositions(1, 5);

      // 2. Map Summary Data (Snake Case -> Camel Case)
      const mappedMetrics: Metrics = {
        pnl: summaryRaw.total_pnl,
        totalTrades: summaryRaw.total_trades,
        marginHealth: summaryRaw.USDT,
        maxDrawdown: summaryRaw.max_drawdown_abs,
      };

      // 3. Map Trades Data
      // Note: Backend 'trades' is an array inside an object
      const mappedTrades: Trade[] = positionsRaw.trades.map(
        (t: any, index: number) => ({
          id: String(index), // Using index since ID isn't in JSON, or use a UUID
          coin: t.symbol.split("/")[0], // Converts "ADA/USDT" to "ADA"
          type: t.side.toUpperCase() as "BUY" | "SELL",
          price: t.entry_price,
          profit: t.pnl,
          timestamp: new Date(t.exit_time),
        }),
      );

      // 4. Set State
      setMetrics(mappedMetrics);
      setRecentTrades(mappedTrades);
    } catch (error) {
      console.error("Error mapping dashboard data:", error);
    }
  };

  const handleStatus = async () => {
    try {
      const response = await api.get<BotResponse>("/bot/status");
      const statusFromServer = response.data.status;

      setBotStatus(statusFromServer);
    } catch (error: any) {
      console.error("Error Starting the bot:", error);

      setBotStatus("Error");
    }
  };

  const handleStart = async () => {
    try {
      const response = await api.post<BotResponse>("/bot/start");
      const statusFromServer = response.data.status;

      console.log(statusFromServer);

      setBotStatus(statusFromServer);
    } catch (error: any) {
      console.error("Error Starting the bot:", error);

      setBotStatus("Error");
    }
  };

  const handleRestart = async () => {
    try {
      const response = await api.post<BotResponse>("/bot/restart");
      const statusFromServer = response.data.status;

      setBotStatus(statusFromServer);
    } catch (error: any) {
      console.error("Error Starting the bot:", error);

      setBotStatus("Error");
    }
    setTimeout(() => setBotStatus("Online"), 2000);
  };

  const handleStop = async () => {
    try {
      const response = await api.post<BotResponse>("/bot/stop");
      const statusFromServer = response.data.status;

      console.log(statusFromServer);

      setBotStatus(statusFromServer);
    } catch (error: any) {
      console.error("Error Starting the bot:", error);

      setBotStatus("Error");
    }
  };

  const formatTime = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  const getStatusColor = (): string => {
    switch (botStatus) {
      case "Online":
        return "#c8f04a";
      case "Warning":
        return "#f0a04a";
      case "Error":
        return "#f04a4a";
      default:
        return "#666";
    }
  };

  const getMarginHealthColor = (health: number): string => {
    if (health >= 70) return "#c8f04a";
    if (health >= 40) return "#f0a04a";
    return "#f04a4a";
  };

  useEffect(() => {
    if (hasRun.current) return;

    handleStatus();
    settingData();

    hasRun.current = true;
  }, []);

  return (
    <div className="home-container">
      {/* Dashboard Metrics */}
      <section className="dashboard-section">
        <div className="metrics-grid">
          {/* PnL Card */}
          <div className="metric-card pnl-card">
            <div className="metric-header">
              <span className="metric-label">Profit & Loss</span>
              {metrics.pnl >= 0 ? (
                <TrendingUp className="metric-icon positive" size={20} />
              ) : (
                <TrendingDown className="metric-icon negative" size={20} />
              )}
            </div>
            <div className="metric-value">
              <span className={metrics.pnl >= 0 ? "positive" : "negative"}>
                {metrics.pnl >= 0 ? "+" : ""}$
                {metrics.pnl.toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </span>
            </div>
            <div className="metric-subtext">Total unrealized</div>
          </div>

          {/* Total Trades Card */}
          <div className="metric-card">
            <div className="metric-header">
              <span className="metric-label">Total Trades</span>
              <Activity className="metric-icon" size={20} />
            </div>
            <div className="metric-value">
              <span>{metrics.totalTrades.toLocaleString()}</span>
            </div>
            <div className="metric-subtext">All-time executions</div>
          </div>

          {/* Margin Health Card */}
          <div className="metric-card margin-card">
            <div className="metric-header">
              <span className="metric-label">Margin Health</span>
              <Shield className="metric-icon" size={20} />
            </div>
            <div className="margin-bar-container">
              <div className="margin-bar-background">
                <div
                  className="margin-bar-fill"
                  style={{
                    width: `${metrics.marginHealth}%`,
                    background: getMarginHealthColor(metrics.marginHealth),
                  }}
                />
              </div>
              <div
                className="margin-percentage"
                style={{ color: getMarginHealthColor(metrics.marginHealth) }}
              >
                {metrics.marginHealth.toFixed(1)}%
              </div>
            </div>
            <div className="metric-subtext">Collateral ratio</div>
          </div>

          {/* Max Drawdown Card */}
          <div className="metric-card drawdown-card">
            <div className="metric-header">
              <span className="metric-label">Max Drawdown</span>
              <AlertTriangle className="metric-icon warning" size={20} />
            </div>
            <div className="metric-value">
              <span className="negative">
                {metrics.maxDrawdown.toFixed(1)}%
              </span>
            </div>
            <div className="metric-subtext">Peak to trough</div>
          </div>
        </div>
      </section>

      {/* Activity Feed */}
      <section className="activity-section">
        <div className="section-header">
          <h2 className="section-title">Recent Activity</h2>
          <span className="activity-count">{recentTrades.length} trades</span>
        </div>

        <div className="activity-feed">
          {recentTrades.map((trade) => (
            <div key={trade.id} className="trade-item">
              <div className="trade-left">
                <div className={`trade-type ${trade.type.toLowerCase()}`}>
                  {trade.type}
                </div>
                <div className="trade-coin">{trade.coin}</div>
              </div>

              <div className="trade-middle">
                <div className="trade-price">
                  $
                  {trade.price.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                  })}
                </div>
              </div>

              <div className="trade-right">
                <div
                  className={`trade-profit ${trade.profit >= 0 ? "positive" : "negative"}`}
                >
                  {trade.profit >= 0 ? "+" : ""}$
                  {Math.abs(trade.profit).toFixed(2)}
                </div>
                <div className="trade-time">{formatTime(trade.timestamp)}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom Control Bar */}
      <div className="control-bar">
        <div className="control-status">
          <div
            className={`status-indicator ${botStatus === "online" ? "pulse" : ""}`}
            style={{ background: getStatusColor() }}
          />
          <span className="status-text" style={{ color: getStatusColor() }}>
            Bot Status: <strong>{botStatus.toUpperCase()}</strong>
          </span>
        </div>

        <div className="control-actions">
          <button
            className="control-btn start-btn"
            onClick={handleStart}
            disabled={botStatus === "online"}
          >
            Start
          </button>
          <button
            className="control-btn restart-btn"
            onClick={handleRestart}
            disabled={botStatus === "offline"}
          >
            Restart
          </button>
          <button
            className="control-btn stop-btn"
            onClick={handleStop}
            disabled={botStatus === "offline"}
          >
            Stop
          </button>
        </div>
      </div>
    </div>
  );
}

export default Home;
