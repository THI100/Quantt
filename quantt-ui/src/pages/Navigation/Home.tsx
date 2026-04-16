import React, { useState, useEffect } from "react";
import "../localassets/Home.css";
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Shield,
  AlertTriangle,
} from "lucide-react";

import api from "../../../api/axiosInstance.js";

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

type BotStatus = "online" | "offline" | "warning" | "error";

function Home() {
  const [botStatus, setBotStatus] = useState<BotStatus>("offline");
  const [metrics, setMetrics] = useState<Metrics>({
    pnl: 2847.32,
    totalTrades: 1247,
    marginHealth: 78.5,
    maxDrawdown: -12.3,
  });

  const [recentTrades, setRecentTrades] = useState<Trade[]>([
    {
      id: "1",
      coin: "BTC/USDT",
      type: "BUY",
      price: 43250.5,
      profit: 125.8,
      timestamp: new Date(Date.now() - 1000 * 60 * 5),
    },
    {
      id: "2",
      coin: "ETH/USDT",
      type: "SELL",
      price: 2280.3,
      profit: -32.15,
      timestamp: new Date(Date.now() - 1000 * 60 * 12),
    },
    {
      id: "3",
      coin: "SOL/USDT",
      type: "BUY",
      price: 98.75,
      profit: 45.6,
      timestamp: new Date(Date.now() - 1000 * 60 * 18),
    },
    {
      id: "4",
      coin: "BNB/USDT",
      type: "SELL",
      price: 312.4,
      profit: 78.2,
      timestamp: new Date(Date.now() - 1000 * 60 * 25),
    },
    {
      id: "5",
      coin: "ADA/USDT",
      type: "BUY",
      price: 0.52,
      profit: -8.5,
      timestamp: new Date(Date.now() - 1000 * 60 * 33),
    },
  ]);

  const handleStart = async () => {
    try {
      const response = await api.post<BotResponse>("/bot/start");
      const statusFromServer = response.data.status;

      console.log(statusFromServer);

      setBotStatus(statusFromServer);
    } catch (error: any) {
      console.error("Error Starting the bot:", error);

      setBotStatus("error");
    }
  };

  const handleRestart = () => {
    setBotStatus("warning");
    setTimeout(() => setBotStatus("online"), 2000);
  };

  const handleStop = () => {
    setBotStatus("offline");
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
      case "online":
        return "#c8f04a";
      case "warning":
        return "#f0a04a";
      case "error":
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
