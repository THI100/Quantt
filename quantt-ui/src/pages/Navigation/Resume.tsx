import React, { useEffect, useState } from "react";
import "../localassets/Resume.css";

export default function Resume() {
  // Mock state - in a real app, you'd fetch from your @r_route endpoints
  const [data, setData] = useState({
    summary: { totalTrades: 154, netProfit: "+$12,450.00" },
    bestWorst: { best: "+$1,200", worst: "-$450" },
    winRate: "68.5%",
    holdTime: "4h 22m",
    maxDrawdown: "4.2%",
    sharpe: "2.1",
    streaks: { winning: 8, losing: 2 },
  });

  return (
    <div className="home-container">
      <div className="activity-section">
        <div className="section-header">
          <h2 className="section-title">Performance Resume</h2>
          <span className="activity-count">ID: REPORT_2026_A</span>
        </div>

        {/* Primary Overview */}
        <div className="metrics-grid">
          <div className="metric-card highlight-blue">
            <div className="metric-header">
              <span className="metric-label">Total Summary</span>
              <i className="metric-icon positive">↗</i>
            </div>
            <div className="metric-value">
              <span>{data.summary.netProfit}</span>
            </div>
            <div className="metric-subtext">
              {data.summary.totalTrades} Executed Trades
            </div>
          </div>

          <div className="metric-card highlight-purple">
            <div className="metric-header">
              <span className="metric-label">Win Rate</span>
              <i className="metric-icon positive">★</i>
            </div>
            <div className="metric-value">
              <span className="positive">{data.winRate}</span>
            </div>
            <div className="metric-subtext">Success Probability</div>
          </div>

          <div className="metric-card">
            <div className="metric-header">
              <span className="metric-label">Risk (Sharpe)</span>
            </div>
            <div className="metric-value">
              <span>{data.sharpe}</span>
            </div>
            <div className="metric-subtext">Risk-Adjusted Return</div>
          </div>
        </div>

        {/* Detailed Analytics Group */}
        <div className="section-header" style={{ marginTop: "40px" }}>
          <h2 className="section-title">Advanced Metrics</h2>
        </div>

        <div className="activity-feed">
          <div className="trade-item">
            <div className="trade-left">
              <span className="trade-type buy">Best Trade</span>
              <span className="trade-coin">{data.bestWorst.best}</span>
            </div>
            <div className="trade-middle">
              <span className="trade-price">Peak Execution</span>
            </div>
            <div className="trade-right">
              <span className="trade-profit positive">MAX GAIN</span>
            </div>
          </div>

          <div className="trade-item">
            <div className="trade-left">
              <span className="trade-type sell">Worst Trade</span>
              <span className="trade-coin">{data.bestWorst.worst}</span>
            </div>
            <div className="trade-middle">
              <span className="trade-price">Stop Loss Triggered</span>
            </div>
            <div className="trade-right">
              <span className="trade-profit negative">MAX LOSS</span>
            </div>
          </div>

          <div className="trade-item">
            <div className="trade-left">
              <span className="trade-type highlight-silver">Drawdown</span>
              <span className="trade-coin">{data.maxDrawdown}</span>
            </div>
            <div className="trade-middle">
              <span className="trade-price">Avg Hold: {data.holdTime}</span>
            </div>
            <div className="trade-right">
              <div className="trade-profit" style={{ color: "#888" }}>
                Safety Margin
              </div>
            </div>
          </div>

          <div className="trade-item">
            <div className="trade-left">
              <span className="trade-type buy">Streaks</span>
              <span className="trade-coin">
                W: {data.streaks.winning} / L: {data.streaks.losing}
              </span>
            </div>
            <div className="trade-middle">
              <span className="trade-price">Consecutive Performance</span>
            </div>
            <div className="trade-right">
              <span
                className="status-indicator pulse"
                style={{ background: "#c8f04a" }}
              ></span>
            </div>
          </div>
        </div>
      </div>

      {/* Control Bar for Report Actions */}
      <div className="control-bar">
        <div className="control-status">
          <div
            className="status-indicator"
            style={{ background: "#c8f04a" }}
          ></div>
          <span className="status-text">
            Status: <strong>Report Finalized</strong>
          </span>
        </div>
        <div className="control-actions">
          <button className="control-btn restart-btn">Export PDF</button>
          <button className="control-btn start-btn">Refresh Data</button>
        </div>
      </div>
    </div>
  );
}
