import React, { useState, useEffect, useRef } from "react";
import "../localassets/Setup.css";
import api from "../../../api/axiosInstance.js";

export default function Setup() {
  // State for Trading Config
  const [trading, setTrading] = useState({
    is_demo_enabled: true,
    timeframe: "15m",
    exchange: "binance",
    future_spot: "future",
    list_of_interest: ["BTC/USDT", "ETH/USDT", "BNB/USDT"],
    list_of_parameters: [
      "MACD",
      "RSI",
      "SMR",
      "TnK",
      "EMA",
      "ATR",
      "DSCP",
      "SMR",
    ],
  });

  // State for Risk Config
  const [risk, setRisk] = useState({
    risk_reward_ratio: 2.0,
    acceptable_confidence: 40,
    atr_multiplier: 0.4,
    maximum_loss: 0.15,
    percentage_of_capital_per_trade: 0.02,
    leverage: 50,
    cross_isolated: "cross",
  });

  const handleUpdate = async (mode: string) => {
    try {
      const raw = api.put("/config/${mode}", { params: mode });
    } catch (error) {
      console.error(
        "The reason that prevented the system from updating the initial parameters:",
        error,
      );
    }
  };

  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;

    const createProfiles = async (mode: string) => {
      try {
        const raw = api.get("/config/${mode}");
        hasRun.current = true;
      } catch (error) {
        console.error(
          "The reason that prevented the system from loading the initial parameters:",
          error,
        );
        hasRun.current = false;
      }
    };
  });

  return (
    <div className="home-container">
      <div className="section-header">
        <h2 className="section-title">System Configuration</h2>
        <span className="activity-count">V0.0.x-DEV</span>
      </div>

      <div className="setup-grid">
        {/* Panel 1: Trading Configuration (Blue Theme) */}
        <div className="config-panel highlight-blue-border">
          <div className="panel-header">
            <span className="panel-icon blue-text">◈</span>
            <h3>Trading Engine</h3>
          </div>

          <form className="setup-form">
            <div className="input-group">
              <label htmlFor="execution-mode">Execution Mode</label>
              <div className="toggle-wrapper">
                <input
                  id="execution-mode"
                  type="checkbox"
                  checked={trading.is_demo_enabled}
                  onChange={(e) =>
                    setTrading({
                      ...trading,
                      is_demo_enabled: e.target.checked,
                    })
                  }
                />
                <span className="toggle-label">Demo / Paper Trading</span>
              </div>
            </div>

            <div className="input-row">
              <div className="input-group">
                <label htmlFor="timeframe">Timeframe</label>
                <input
                  id="timeframe"
                  type="text"
                  value={trading.timeframe}
                  className="terminal-input"
                />
              </div>
              <div className="input-group">
                <label htmlFor="market">Market</label>
                <select
                  id="market"
                  value={trading.future_spot}
                  className="terminal-input"
                >
                  <option value="future">Future</option>
                  <option value="spot">Spot</option>
                </select>
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="exchange-entity">Exchange Entity</label>
              <select
                id="exchange-entity"
                value={trading.exchange}
                className="terminal-input"
              >
                <option value="binance">Binance</option>
                <option value="bybit">Bybit</option>
                <option value="okx">OKX</option>
              </select>
            </div>

            <div className="input-group">
              <label htmlFor="assets-of-interest">
                Assets of Interest (Comma separated)
              </label>
              <textarea
                id="assets-of-interest"
                className="terminal-input"
                defaultValue={trading.list_of_interest.join(", ")}
              />
            </div>

            <div className="">
              <label htmlFor="configuration-of-analysis">
                Parameters for Analysis
              </label>
              <input
                id="macd"
                type="checkbox"
                value="MACD"
                className="macd_check"
              />
              <input
                id="ichimoku"
                type="checkbox"
                value="Ichimoku"
                className="ichimoku_check"
              />
              <input
                id="rsi"
                type="checkbox"
                value="RSI"
                className="rsi_check"
              />
              <input
                id="tnk"
                type="checkbox"
                value="TnK"
                className="tnk_check"
              />
              <input
                id="ema"
                type="checkbox"
                value="EMA"
                className="ema_check"
              />
              <input
                id="atr"
                type="checkbox"
                value="ATR"
                className="atr_check"
              />
              <input
                id="dcsp"
                type="checkbox"
                value="DCSP"
                className="dscp_check"
              />
              <input
                id="smr"
                type="checkbox"
                value="SMR"
                className="smr_check"
              />
            </div>

            <button
              type="button"
              className="control-btn restart-btn full-width"
              onClick={handleUpdate("trading")}
            >
              Patch Engine
            </button>
          </form>
        </div>

        {/* Panel 2: Risk Configuration (Purple Theme) */}
        <div className="config-panel highlight-purple-border">
          <div className="panel-header">
            <span className="panel-icon purple-text">🛡</span>
            <h3>Risk Parameters</h3>
          </div>

          <form className="setup-form">
            <div className="input-row">
              <div className="input-group">
                <label htmlFor="risk-reward">Risk/Reward</label>
                <input
                  id="risk-reward"
                  type="number"
                  step="0.1"
                  value={risk.risk_reward_ratio}
                  className="terminal-input"
                />
              </div>
              <div className="input-group">
                <label htmlFor="leverage">Leverage</label>
                <input
                  id="leverage"
                  type="number"
                  value={risk.leverage}
                  className="terminal-input"
                />
              </div>
            </div>

            <div className="input-row">
              <div className="input-group">
                <label htmlFor="max-loss">Max Loss (%)</label>
                <input
                  id="max-loss"
                  type="number"
                  step="0.01"
                  value={risk.maximum_loss}
                  className="terminal-input"
                />
              </div>
              <div className="input-group">
                <label htmlFor="margin-type">Margin Type</label>
                <select
                  id="margin-type"
                  value={risk.cross_isolated}
                  className="terminal-input"
                >
                  <option value="cross">Cross</option>
                  <option value="isolated">Isolated</option>
                </select>
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="confidence-threshold">
                Confidence Threshold ({risk.acceptable_confidence}%)
              </label>
              <input
                id="confidence-threshold"
                type="range"
                min="0"
                max="100"
                value={risk.acceptable_confidence}
                className="terminal-slider"
              />
            </div>

            <div className="input-group">
              <label htmlFor="capital-per-trade">Capital Per Trade</label>
              <input
                id="capital-per-trade"
                type="number"
                step="0.01"
                value={risk.percentage_of_capital_per_trade}
                className="terminal-input"
              />
            </div>

            <button type="button" className="control-btn start-btn full-width">
              Patch Risk Profile
            </button>
          </form>
        </div>
      </div>

      {/* Bottom Global Actions */}
      <div className="control-bar">
        <div className="control-status">
          <div className="status-indicator pulse highlight-silver-bg"></div>
          <span className="status-text">
            Ready to <strong>Commit Changes</strong>
          </span>
        </div>
        <div className="control-actions">
          <button
            className="control-btn stop-btn"
            onClick={handleUpdate("risk")}
          >
            Reset to Defaults
          </button>
        </div>
      </div>
    </div>
  );
}
