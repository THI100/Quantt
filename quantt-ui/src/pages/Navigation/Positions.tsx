import React, { useState, useEffect } from "react";
import api from "../../../api/axiosInstance.js";
import "../localassets/Positions.css";

export default function Positions() {
  const [deleteForm, setDeleteForm] = useState({ id: "", symbol: "" });
  const [selectForm, setSelectForm] = useState({ symbol: "" });

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
  ]);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const bottom =
      e.currentTarget.scrollHeight - e.currentTarget.scrollTop ===
      e.currentTarget.clientHeight;
    if (bottom) {
      console.log("Fetching next page...");
    }
  };

  const handleDelete = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log(
      `Calling DELETE /positions/${deleteForm.symbol} with ID: ${deleteForm.id}`,
    );
    try {
      const deletionRaw = await api.delete("/positions", {
        params: { symbol: deleteForm.symbol, id: deleteForm.id },
      });
      console.log("Status:", deletionRaw);
    } catch (error) {
      console.error(
        `Error happened with Deletion of ${deleteForm.symbol} and ${deleteForm.id}:`,
        error,
      );
    }
  };

  const handleSelection = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const positionsRaw = await api.get("/positions", {
        params: { symbol: selectForm.symbol },
      });
    } catch (error) {
      console.error("Error happened with selection of symbol:", error);
    }
  };

  return (
    <div className="home-container" onScroll={handleScroll}>
      {/* Superior Region: Position Management Form */}
      <div className="management-section">
        <div className="delete-card">
          <div className="card-header-mini">
            <span className="purple-text">◈</span>
            <h3>Terminator Module</h3>
            <span className="silver-subtext">Manual Position Deletion</span>
          </div>
          <form className="delete-inline-form" onSubmit={handleDelete}>
            <div className="input-field">
              <label>Position ID</label>
              <input
                type="text"
                placeholder="Ex: 1024"
                value={deleteForm.id}
                onChange={(e) =>
                  setDeleteForm({ ...deleteForm, id: e.target.value })
                }
              />
            </div>
            <div className="input-field">
              <label>Symbol</label>
              <input
                type="text"
                placeholder="BTC/USDT"
                value={deleteForm.symbol}
                onChange={(e) =>
                  setDeleteForm({ ...deleteForm, symbol: e.target.value })
                }
              />
            </div>
            <button type="submit" className="control-btn stop-btn">
              Terminate Position
            </button>
          </form>
        </div>
      </div>

      <div className="section-header">
        <h2 className="section-title">Historical Positions</h2>
        <form className="delete-inline-form" onSubmit={handleDelete}>
          <div className="input-field">
            <label>Symbol</label>
            <input
              type="text"
              placeholder="BTC/USDT"
              value={selectForm.symbol}
              onChange={(e) =>
                setDeleteForm({ ...selectForm, symbol: e.target.value })
              }
            />
          </div>
          <button type="submit" className="control-btn">
            Search
          </button>
        </form>
      </div>

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
              <span className="pos-id-tag">#{pos.id}</span>
            </div>

            <div className="pos-price">
              <span className="label-mobile">Entry:</span>
              <span className="mono-value"> ${pos.price}</span>
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
