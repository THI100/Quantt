import React, { useState, useEffect, useRef } from "react";
import "../localassets/Setup.css";
import api from "../../../api/axiosInstance.js";

export default function Setup() {
  const [trading, setTrading] = useState({
    is_demo_enabled: false,
    timeframe: "",
    exchange: "",
    future_spot: "future",
    list_of_interest: [],
    list_of_parameters: [],
  });

  const [risk, setRisk] = useState({
    risk_reward_ratio: 0,
    acceptable_confidence: 0,
    atr_multiplier: 0,
    maximum_loss: 0,
    percentage_of_capital_per_trade: 0,
    leverage: 1,
    cross_isolated: "",
  });

  // Fixed the immediate execution bug and the messy parameter logic
  const handleUpdate = (mode: "trading" | "risk") => async () => {
    try {
      const payload = mode === "trading" ? trading : risk;
      await api.put(`/config/${mode}`, payload);
      console.log(`${mode} configuration updated successfully.`);
    } catch (error) {
      console.error(`Failed to update ${mode} parameters:`, error);
    }
  };

  const handleCheckboxChange = (param: string) => {
    const updatedList = trading.list_of_parameters.includes(param)
      ? trading.list_of_parameters.filter((p) => p !== param)
      : [...trading.list_of_parameters, param];

    setTrading({ ...trading, list_of_parameters: updatedList });
  };

  const stat = useRef(false);

  useEffect(() => {
    if (stat.current) return;

    const fetchConfig = async () => {
      try {
        stat.current = true;
        const tradingRes = await api.get("/config/trading");
        const riskRes = await api.get("/config/risk");
        if (tradingRes.data) setTrading(tradingRes.data);
        if (riskRes.data) setRisk(riskRes.data);
      } catch (error) {
        console.error("Error loading initial parameters:", error);
        stat.current = false;
      }
    };

    fetchConfig();
  }, []); // Empty array ensures this only runs once

  return (
    <div className="home-container">
      <div className="section-header">
        <h2 className="section-title">System Configuration</h2>
        <span className="activity-count">V0.0.x-DEV</span>
      </div>

      <div className="setup-grid">
        {/* Panel 1: Trading Configuration */}
        <div className="config-panel highlight-blue-border">
          <div className="panel-header">
            <span className="panel-icon blue-text">◈</span>
            <h3>Trading Engine</h3>
          </div>

          <form className="setup-form">
            <div className="input-group">
              <label>Execution Mode</label>
              <div className="toggle-wrapper">
                <input
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
                <label>Timeframe (e.g: 30s, 2m, 15m, 1h)</label>
                <input
                  type="text"
                  value={trading.timeframe}
                  className="terminal-input"
                  onChange={(e) =>
                    setTrading({ ...trading, timeframe: e.target.value })
                  }
                />
              </div>
              <div className="input-group">
                <label>Market</label>
                <select
                  value={trading.future_spot}
                  className="terminal-input"
                  onChange={(e) =>
                    setTrading({ ...trading, future_spot: e.target.value })
                  }
                >
                  <option value="future">Future</option>
                  <option value="spot">Spot</option>
                </select>
              </div>
            </div>

            <div className="input-group">
              <label>Exchange</label>
              <select
                value={trading.exchange}
                className="terminal-input"
                onChange={(e) =>
                  setTrading({ ...trading, exchange: e.target.value })
                }
              >
                <option value="binance">Binance</option>
                <option value="bybit">Bybit</option>
                <option value="okx">OKX</option>
                <option value="mexc">Mexc</option>
              </select>
            </div>

            <div className="input-group">
              <label>Assets (Comma separated)</label>
              <textarea
                className="terminal-input"
                value={trading.list_of_interest.join(", ")}
                onChange={(e) =>
                  setTrading({
                    ...trading,
                    list_of_interest: e.target.value.split(", "),
                  })
                }
              />
            </div>

            <div className="parameter-grid-container">
              <label className="group-label">Parameters for Analysis</label>
              <div className="checkbox-grid">
                {[
                  "MACD",
                  "RSI",
                  "TnK",
                  "EMA",
                  "ATR",
                  "DSCP",
                  "SMR",
                  "PPF",
                  "OBV",
                  "ADX",
                  "BB",
                  "VWAP",
                  "ST",
                  "ROC",
                ].map((p) => (
                  <label key={p} className="checkbox-item">
                    <input
                      type="checkbox"
                      checked={trading.list_of_parameters.includes(p)}
                      onChange={() => handleCheckboxChange(p)}
                    />
                    <span>{p}</span>
                  </label>
                ))}
              </div>
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
                  onChange={(e) =>
                    setRisk({ ...risk, risk_reward_ratio: e.target.value })
                  }
                />
              </div>
              <div className="input-group">
                <label htmlFor="leverage">Leverage (x)</label>
                <input
                  id="leverage"
                  type="number"
                  value={risk.leverage}
                  className="terminal-input"
                  onChange={(e) =>
                    setRisk({ ...risk, leverage: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="input-row">
              <div className="input-group">
                <label htmlFor="max-loss">Max Loss (decimal)</label>
                <input
                  id="max-loss"
                  type="number"
                  step="0.01"
                  value={risk.maximum_loss}
                  className="terminal-input"
                  onChange={(e) =>
                    setRisk({ ...risk, maximum_loss: e.target.value })
                  }
                />
              </div>
              <div className="input-group">
                <label htmlFor="margin-type">Margin Type</label>
                <select
                  id="margin-type"
                  value={risk.cross_isolated}
                  className="terminal-input"
                  onChange={(e) =>
                    setRisk({ ...risk, cross_isolated: e.target.value })
                  }
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
                onChange={(e) =>
                  setRisk({ ...risk, acceptable_confidence: e.target.value })
                }
              />
            </div>

            <div className="input-group">
              <label htmlFor="capital-per-trade">
                Capital Per Trade (decimal)
              </label>
              <input
                id="capital-per-trade"
                type="number"
                step="0.01"
                value={risk.percentage_of_capital_per_trade}
                className="terminal-input"
                onChange={(e) =>
                  setRisk({
                    ...risk,
                    percentage_of_capital_per_trade: e.target.value,
                  })
                }
              />
            </div>

            <button
              type="button"
              className="control-btn start-btn full-width"
              onClick={handleUpdate("risk")}
            >
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
          <button className="control-btn stop-btn">Reset to Defaults</button>
        </div>
      </div>
    </div>
  );
}
