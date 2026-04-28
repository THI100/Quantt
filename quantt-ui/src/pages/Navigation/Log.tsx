import { useState, useEffect, useRef } from "react";
import api from "../../../api/axiosInstance.js";
import "../localassets/Log.css";

export default function Log() {
  const [logs, setLogs] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const logEndRef = useRef(null);

  // Get the base URL from your axios instance
  const baseURL = api.defaults.baseURL || "";

  useEffect(() => {
    const eventSource = new EventSource(`${baseURL}/bot/logging`);

    // Log 1: Check if the connection actually opens
    eventSource.onopen = () => {
      console.log("SSE: Connection established");
      setIsConnected(true);
    };

    // Log 2: Use addEventListener('message') to be safer
    const messageHandler = (event) => {
      console.log("SSE: Raw data received ->", event.data); // If this doesn't log, it's a backend formatting issue
      try {
        const newLog = JSON.parse(event.data);
        setLogs((prev) => [...prev, newLog]);
      } catch (err) {
        console.error("SSE: Parse error ->", err);
      }
    };

    eventSource.addEventListener("message", messageHandler);

    // Log 3: Check for errors (like 401 Unauthorized)
    eventSource.onerror = (err) => {
      console.error("SSE: Connection error/closed", err);
      setIsConnected(false);
    };

    return () => {
      eventSource.removeEventListener("message", messageHandler);
      eventSource.close();
    };
  }, [baseURL]);

  const clearLogs = () => setLogs([]);

  return (
    <div className="home-container logs-container">
      <header className="section-header">
        <h2 className="section-title">System Logs</h2>
        <div className="terminal-controls">
          <span className="refresh-status">
            {isConnected ? "● Live Streaming" : "○ Disconnected"}
          </span>
          <button
            className="control-btn"
            onClick={clearLogs}
            style={{ padding: "6px 12px", marginLeft: "10px" }}
          >
            Clear Console
          </button>
        </div>
      </header>

      <div className="terminal-box">
        <div className="terminal-header">
          <div className="trade-coin">console_output.log</div>
          <div className="activity-count">{logs.length} Lines</div>
        </div>

        <div className="log-content">
          {logs.map((log, index) => (
            <div key={index} className="log-entry">
              {/* Note: changed log.timestamp to log.time based on your API response */}
              <span className="log-timestamp">[{log.time}]</span>
              <span className={`log-message ${log.level?.toLowerCase()}`}>
                {log.message}
              </span>
            </div>
          ))}
          <div ref={logEndRef} />
        </div>
      </div>

      <div className="control-bar">
        <div className="control-status">
          <div
            className={`status-indicator pulse ${isConnected ? "positive" : "warning"}`}
            style={{ backgroundColor: isConnected ? "#c8f04a" : "#f0a04a" }}
          ></div>
          <span className="status-text">
            STREAM STATUS:{" "}
            <strong>{isConnected ? "ACTIVE" : "RECONNECTING"}</strong>
          </span>
        </div>
      </div>
    </div>
  );
}
