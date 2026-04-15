import React, { useState } from "react";
import "../localassets/Graphs.css";

// Skeleton Component for the actual Graphic engine
function GraphPlaceholder({
  title,
  colorClass,
}: {
  title: string;
  colorClass: string;
}) {
  return (
    <div className={`graph-skeleton-box ${colorClass}`}>
      <div className="skeleton-line-chart">
        {/* This is where your Canvas/SVG will go */}
        <div className="pulse-line"></div>
      </div>
      <span className="skeleton-label">{title}</span>
    </div>
  );
}

export default function Graphs() {
  const [graphList, setGraphList] = useState([
    { id: 1, name: "BTC/USDT - 15m Trend", type: "blue" },
    { id: 2, name: "RSI / MACD Indicators", type: "purple" },
    { id: 3, name: "Volume Delta", type: "blue" },
    { id: 4, name: "Liquidity Heatmap", type: "purple" },
  ]);

  const handleInfiniteScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const target = e.currentTarget;
    if (target.scrollHeight - target.scrollTop === target.clientHeight) {
      // Logic to fetch more graph data/skeletons
      console.log("Loading more analytics...");
    }
  };

  return (
    <div className="home-container">
      <div className="section-header">
        <h2 className="section-title">Visual Analytics</h2>
        <div className="activity-count">Real-time Stream</div>
      </div>

      {/* Top Fixed Statistics Grid */}
      <div className="metrics-grid">
        <div className="metric-card highlight-blue">
          <div className="metric-header">
            <span className="metric-label">Volatility Index</span>
          </div>
          <div className="metric-value">
            <span>0.84%</span>
          </div>
          <GraphPlaceholder title="VIX Mini" colorClass="blue-tint" />
        </div>
        <div className="metric-card highlight-purple">
          <div className="metric-header">
            <span className="metric-label">Market Momentum</span>
          </div>
          <div className="metric-value positive">
            <span>Bullish</span>
          </div>
          <GraphPlaceholder title="Momentum" colorClass="purple-tint" />
        </div>
      </div>

      {/* Infinite Scrolling Graph Section */}
      <div className="graph-feed-container" onScroll={handleInfiniteScroll}>
        <h3 className="sub-section-title">Historical Trends & Indicators</h3>

        <div className="infinite-graph-list">
          {graphList.map((graph) => (
            <div key={graph.id} className="graph-item-card">
              <div className="graph-item-header">
                <span
                  className={`status-indicator ${graph.type === "blue" ? "blue-bg" : "purple-bg"}`}
                ></span>
                <h4>{graph.name}</h4>
                <span className="trade-time">Live Feed</span>
              </div>
              <div className="graph-content-area">
                {/* Placeholder for the real React component later */}
                <div className="actual-graph-component-skeleton">
                  <p className="silver-text">
                    Component: DynamicGraph({graph.type})
                  </p>
                </div>
              </div>
              <div className="graph-item-footer">
                <button className="control-btn restart-btn">Expand</button>
                <button className="control-btn start-btn">Settings</button>
              </div>
            </div>
          ))}
        </div>

        <div className="loading-trigger">
          <span className="status-indicator pulse highlight-silver-bg"></span>
          <p>Syncing additional datasets...</p>
        </div>
      </div>

      {/* Control Bar */}
      <div className="control-bar">
        <div className="control-status">
          <div className="status-indicator positive"></div>
          <span className="status-text">
            Engine: <strong>Graphics Ready</strong>
          </span>
        </div>
        <div className="control-actions">
          <button className="control-btn stop-btn">Clear Buffer</button>
        </div>
      </div>
    </div>
  );
}
