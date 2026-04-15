import React, { useState, useEffect } from "react";
import "../localassets/Positions.css";

export default function Positions() {
  // Simulated state for infinite scroll
  const [positions, setPositions] = useState([
    {
      id: 1,
      coin: "BTC/USDT",
      price: "64,230.50",
      pnl: "+12.4%",
      tp: "68,000",
      sl: "61,000",
      time: "2026-04-14 10:20",
    },
    {
      id: 2,
      coin: "ETH/USDT",
      price: "3,450.20",
      pnl: "-2.1%",
      tp: "3,800",
      sl: "3,300",
      time: "2026-04-14 09:15",
    },
    {
      id: 3,
      coin: "SOL/USDT",
      price: "145.10",
      pnl: "+5.7%",
      tp: "160",
      sl: "138",
      time: "2026-04-14 08:45",
    },
    {
      id: 4,
      coin: "LINK/USDT",
      price: "18.25",
      pnl: "+0.8%",
      tp: "22",
      sl: "17",
      time: "2026-04-14 07:30",
    },
  ]);

  // Simple scroll handler logic could be added here to fetch more data
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const bottom =
      e.currentTarget.scrollHeight - e.currentTarget.scrollTop ===
      e.currentTarget.clientHeight;
    if (bottom) {
      console.log("Fetching next page of history...");
      // appendData();
    }
  };

  return (
    <div className="home-container" onScroll={handleScroll}>
      <div className="section-header">
        <h2 className="section-title">Historical Positions</h2>
        <div className="control-status">
          <span className="activity-count">Total: {positions.length}</span>
        </div>
      </div>

      {/* Table Header - Desktop Only */}
      <div className="positions-list-header">
        <span>Asset</span>
        <span>Entry Price</span>
        <span>TP / SL</span>
        <span>PnL</span>
        <span>Timestamp</span>
      </div>

      <div className="infinite-scroll-area">
        {positions.map((pos) => (
          <div key={pos.id} className="position-row-card">
            <div className="pos-asset">
              <span className="trade-type highlight-silver">Spot</span>
              <span className="asset-name">{pos.coin}</span>
            </div>

            <div className="pos-price">
              <span className="label-mobile">Entry:</span>
              <span className="mono-value">${pos.price}</span>
            </div>

            <div className="pos-targets">
              <div className="target-group">
                <span className="tp-text">TP: {pos.tp}</span>
                <span className="sl-text">SL: {pos.sl}</span>
              </div>
            </div>

            <div
              className={`pos-pnl ${pos.pnl.startsWith("+") ? "positive" : "negative"}`}
            >
              {pos.pnl}
            </div>

            <div className="pos-time">{pos.time}</div>
          </div>
        ))}
      </div>

      {/* Fixed Footer Status */}
      <div className="control-bar">
        <div className="control-status">
          <div className="status-indicator pulse highlight-purple-bg"></div>
          <span className="status-text">
            Syncing <strong>History</strong>...
          </span>
        </div>
        <div className="control-actions">
          <button className="control-btn restart-btn">Filter By Date</button>
          <button className="control-btn start-btn">Download CSV</button>
        </div>
      </div>
    </div>
  );
}
