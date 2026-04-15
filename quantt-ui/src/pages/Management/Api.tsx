import React, { useState } from "react";
import "../localassets/Api.css";

export default function Api() {
  const [apiData, setApiData] = useState({
    exchange: "binance",
    apiKey: "",
    apiSecret: "",
  });

  return (
    <div className="home-container">
      <div className="section-header">
        <h2 className="section-title silver-text">Exchange Credentials</h2>
        <span className="activity-count">Security Protocol: AES-256</span>
      </div>

      <div className="vault-container">
        <div className="api-card">
          <div className="api-card-header">
            <div className="security-icon-wrapper">
              <span className="security-icon">🔒</span>
            </div>
            <h3>API Connectivity</h3>
            <p className="silver-subtext">
              These keys are stored locally in the environment configuration.
            </p>
          </div>

          <form className="api-form">
            <div className="input-group">
              <label>Target Exchange</label>
              <select
                className="neutral-input"
                value={apiData.exchange}
                onChange={(e) =>
                  setApiData({ ...apiData, exchange: e.target.value })
                }
              >
                <option value="binance">Binance (Global/US)</option>
                <option value="bybit">Bybit</option>
                <option value="okx">OKX</option>
              </select>
            </div>

            <div className="input-group">
              <label>API Key</label>
              <input
                type="text"
                className="neutral-input"
                placeholder="Enter public key..."
                value={apiData.apiKey}
                onChange={(e) =>
                  setApiData({ ...apiData, apiKey: e.target.value })
                }
              />
            </div>

            <div className="input-group">
              <label>API Secret</label>
              <input
                type="password"
                className="neutral-input"
                placeholder="Enter private secret..."
                value={apiData.apiSecret}
                onChange={(e) =>
                  setApiData({ ...apiData, apiSecret: e.target.value })
                }
              />
            </div>

            <div className="warning-box">
              <span className="warning-text">
                Ensure your API keys have "Spot/Futures Trading" enabled but
                "Withdrawals" DISABLED.
              </span>
            </div>

            <div className="api-actions">
              <button type="button" className="neutral-btn grey-btn">
                Test Connection
              </button>
              <button type="button" className="neutral-btn confirm-btn">
                Save to .env
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Status Bar */}
      <div className="control-bar">
        <div className="control-status">
          <div
            className="status-indicator"
            style={{ background: "#888" }}
          ></div>
          <span className="status-text silver-text">
            Encryption: <strong>Active</strong>
          </span>
        </div>
      </div>
    </div>
  );
}
