import { useState, useEffect, useCallback, useRef } from "react";
import "../localassets/Logs.css";

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [isPolling, setIsPolling] = useState(true);
  const logEndRef = useRef(null);

  // 1. Base function for fetching data (Manual Refresh)
  const fetchLogs = useCallback(async () => {
    try {
      // Replace with your actual API endpoint
      const response = await fetch("/api/logs");
      const data = await response.json();
      setLogs(data);
    } catch (error) {
      console.error("Failed to sync logs:", error);
    }
  }, []);

  // 2. The Auto-Polling function
  const startPolling = useCallback(() => {
    const interval = setInterval(async () => {
      if (isPolling) {
        await fetchLogs();
      }
    }, 5000); // Refreshes every 5 seconds
    return interval;
  }, [isPolling, fetchLogs]);

  // 3. UseEffect to handle lifecycle
  useEffect(() => {
    fetchLogs(); // Initial load
    const intervalId = startPolling();

    return () => clearInterval(intervalId); // Cleanup on unmount
  }, [fetchLogs, startPolling]);

  // Auto-scroll to bottom when logs update
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="home-container logs-container">
      <header className="section-header">
        <h2 className="section-title">System Logs</h2>
        <div className="terminal-controls">
          <span className="refresh-status">
            {isPolling ? "● Live Syncing" : "Paused"}
          </span>
          <button
            className="control-btn start-btn"
            onClick={fetchLogs}
            style={{ padding: "6px 12px" }}
          >
            Refresh Now
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
              <span className="log-timestamp">[{log.timestamp}]</span>
              <span className={`log-message ${log.level}`}>{log.message}</span>
            </div>
          ))}
          <div ref={logEndRef} />
        </div>
      </div>

      {/* Reusing your Control Bar for navigation or global actions */}
      <div className="control-bar">
        <div className="control-status">
          <div
            className={`status-indicator pulse ${isPolling ? "positive" : "warning"}`}
            style={{ backgroundColor: isPolling ? "#c8f04a" : "#f0a04a" }}
          ></div>
          <span className="status-text">
            SYSTEM: <strong>STABLE</strong>
          </span>
        </div>
        <div className="control-actions">
          <button
            className="control-btn stop-btn"
            onClick={() => setIsPolling(!isPolling)}
          >
            {isPolling ? "Stop Polling" : "Resume Polling"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Logs;
