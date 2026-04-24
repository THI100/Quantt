import React, { useState, useEffect, useRef } from "react";
import "../localassets/Api.css";
import api from "../../../api/axiosInstance.js";

export default function Api() {
  const [apiData, setApiData] = useState({
    exchange: "",
    apiKey: "",
    apiSecret: "",
  });

  const [status, setStatus] = useState("Ready");
  const hasRun = useRef(false);

  const handleSend = async () => {
    // Basic validation to prevent empty sends
    if (!apiData.apiKey || !apiData.apiSecret) {
      setStatus("Error: Fields Missing");
      return;
    }

    try {
      setStatus("Updating...");

      // We map camelCase (frontend) to snake_case (backend Pydantic model)
      const payload = {
        api_key: apiData.apiKey,
        api_secret: apiData.apiSecret,
        exchange: apiData.exchange,
      };

      const response = await api.patch("/config/api", payload);

      console.log("Success:", response.data);
      setStatus("Credentials Updated");

      setApiData({ ...apiData, apiKey: "", apiSecret: "" });
    } catch (error) {
      const errorMsg = error.response?.data?.detail || "Update Failed";
      console.error("Backend Error:", errorMsg);
      setStatus(`Error: ${errorMsg}`);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete the configuration?"))
      return;

    try {
      setStatus("Deleting...");
      await api.delete("config/api");
      setApiData({ exchange: "", apiKey: "", apiSecret: "" });
      setStatus("Deleted");
    } catch (error) {
      console.error("Error as deleting the .env file:", error);
      setStatus("Delete Failed");
    }
  };

  // useEffect cannot be directly async. Wrapping the logic inside.
  useEffect(() => {
    if (hasRun.current) return;

    const initApi = async () => {
      try {
        const answer = await api.post("/config/api");
        console.log("Status on api creation:", answer);
      } catch (error) {
        console.error("Error on api .env creation:", error);
      }
    };

    initApi();
    hasRun.current = true;
  }, []);

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

          <form className="api-form" onSubmit={(e) => e.preventDefault()}>
            <div className="input-group">
              <label htmlFor="target-exchange">Target Exchange</label>
              <select
                id="target-exchange"
                className="neutral-input"
                value={apiData.exchange}
                onChange={(e) =>
                  setApiData({ ...apiData, exchange: e.target.value })
                }
              >
                <option value="binance">Binance (Global/US)</option>
                <option value="bybit">Bybit</option>
                <option value="okx">OKX</option>
                <option value="mexc">Mexc</option>
              </select>
            </div>

            <div className="input-group">
              <label htmlFor="api-key">API Key</label>
              <input
                id="api-key"
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
              <label htmlFor="api-secret">API Secret</label>
              <input
                id="api-secret"
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
                "Withdrawals" <strong>DISABLED</strong>.
              </span>
            </div>

            <div className="api-actions">
              <button
                type="button"
                className="neutral-btn grey-btn"
                onClick={handleDelete}
              >
                Delete file
              </button>
              <button
                type="button"
                className="neutral-btn confirm-btn"
                onClick={handleSend}
              >
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
            style={{
              background: status.includes("Error") ? "#ff4d4d" : "#00ff88",
            }}
          ></div>
          <span className="status-text silver-text">
            Encryption: <strong>{status}</strong>
          </span>
        </div>
      </div>
    </div>
  );
}
