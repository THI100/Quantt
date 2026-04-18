import React, { useState, useEffect, useCallback } from "react";
import api from "../../../api/axiosInstance.js";
import "../localassets/Positions.css";

export default function Positions() {
  const [deleteForm, setDeleteForm] = useState({ id: "", symbol: "" });
  const [selectForm, setSelectForm] = useState({ symbol: "" });
  const [positions, setPositions] = useState([]);

  // Pagination & Loading States
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Fetch Positions Logic
   * Wrapped in useCallback to prevent unnecessary re-renders
   */
  const fetchPositions = useCallback(async (pageNum, symbol = "") => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get("/report/trades", {
        params: {
          symbol: symbol || undefined,
          page: pageNum,
          page_size: 20,
        },
      });

      const newTrades = response.data.trades || [];
      const totalPages = response.data.pages || 1;

      setPositions((prev) =>
        pageNum === 1 ? newTrades : [...prev, ...newTrades],
      );
      setHasMore(pageNum < totalPages);
    } catch (err) {
      setError("Failed to load positions.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // 2. Initial load useEffect: Only runs ONCE on mount
  useEffect(() => {
    fetchPositions(1);
  }, [fetchPositions]);

  /**
   * Infinite Scroll Logic
   */
  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    // Trigger when user is 10px from the bottom
    const isNearBottom = scrollHeight - scrollTop <= clientHeight + 10;

    if (isNearBottom && hasMore && !loading) {
      const nextPage = page + 1;
      setPage(nextPage);
      fetchPositions(nextPage, selectForm.symbol);
    }
  };

  /**
   * Delete Logic
   */
  const handleDelete = async (e) => {
    e.preventDefault();
    if (!deleteForm.id || !deleteForm.symbol)
      return alert("Please provide ID and Symbol");

    try {
      await api.delete("/positions", {
        params: { symbol: deleteForm.symbol, id: deleteForm.id },
      });
      // Remove from UI upon success
      setPositions(
        positions.filter((p) => p.id.toString() !== deleteForm.id.toString()),
      );
      setDeleteForm({ id: "", symbol: "" });
      alert("Position terminated successfully.");
    } catch (error) {
      console.error("Deletion error:", error);
      alert("Failed to terminate position.");
    }
  };

  /**
   * Search Logic
   */
  const handleSelection = async (e) => {
    e.preventDefault();
    setPage(1);
    setHasMore(true);
    fetchPositions(1, selectForm.symbol);
  };

  return (
    <div
      className="home-container"
      onScroll={handleScroll}
      style={{ overflowY: "auto", height: "100vh" }}
    >
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
        {/* Fixed: changed onSubmit to handleSelection and corrected the onChange target */}
        <form className="delete-inline-form" onSubmit={handleSelection}>
          <div className="input-field">
            <label>Symbol</label>
            <input
              type="text"
              placeholder="BTC/USDT"
              value={selectForm.symbol}
              onChange={(e) =>
                setSelectForm({ ...selectForm, symbol: e.target.value })
              }
            />
          </div>
          <button type="submit" className="control-btn" disabled={loading}>
            {loading ? "Searching..." : "Search"}
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
        {positions && positions.length > 0
          ? positions.map((pos, index) => (
              // Using a composite key because IDs aren't in your sample JSON
              <div
                key={`${pos.symbol}-${pos.entry_time}-${index}`}
                className="position-row-card"
              >
                <div className="pos-asset">
                  <span className="trade-type highlight-silver">
                    {pos.side.toUpperCase()}
                  </span>
                  <span className="asset-name">{pos.symbol}</span>
                </div>

                <div className="pos-price">
                  <span className="label-mobile">Entry:</span>
                  <span className="mono-value">
                    {" "}
                    ${pos.entry_price.toLocaleString()}
                  </span>
                </div>

                <div className="pos-targets">
                  <div className="target-group">
                    {/* Using exit_price as a placeholder since sample lacks TP/SL */}
                    <span className="tp-text">Exit: {pos.exit_price}</span>
                    <span className="sl-text">
                      Hold: {Math.round(pos.hold_time_sec)}s
                    </span>
                  </div>
                </div>

                <div
                  className={`pos-pnl ${pos.pnl >= 0 ? "positive" : "negative"}`}
                >
                  {pos.pnl >= 0 ? `+${pos.pnl.toFixed(2)}` : pos.pnl.toFixed(2)}
                </div>

                <div className="pos-time">
                  {new Date(pos.entry_time).toLocaleString([], {
                    dateStyle: "short",
                    timeStyle: "short",
                  })}
                </div>
              </div>
            ))
          : !loading && (
              <div className="empty-state">No historical trades found.</div>
            )}
      </div>

      <div className="control-bar">
        <div className="control-status">
          <div
            className={`status-indicator ${loading ? "pulse highlight-purple-bg" : ""}`}
          ></div>
          <span className="status-text">
            {loading ? "Syncing History..." : "System Ready"}
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
