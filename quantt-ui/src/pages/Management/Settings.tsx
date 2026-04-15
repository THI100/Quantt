import React, { useState } from "react";
import "../localassets/Settings.css";

export default function Settings() {
  // Local state for frontend-only settings
  const [uiSettings, setUiSettings] = useState({
    darkMode: true,
    compactMode: false,
    refreshRate: "1s",
    animations: true,
    showNotifications: true,
    soundEffects: false,
  });

  return (
    <div className="home-container">
      <div className="section-header">
        <h2 className="section-title silver-text">Local Preferences</h2>
        <span className="activity-count">Client-Side Only</span>
      </div>

      <div className="settings-wrapper">
        <div className="settings-card">
          {/* Category: Interface */}
          <div className="settings-category">
            <h3 className="category-label">Display & Interface</h3>

            <div className="setting-row">
              <div className="setting-info">
                <span className="setting-name">Compact Dashboard</span>
                <span className="setting-description">
                  Reduce padding and font sizes for high-density data.
                </span>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={uiSettings.compactMode}
                  onChange={() =>
                    setUiSettings({
                      ...uiSettings,
                      compactMode: !uiSettings.compactMode,
                    })
                  }
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-row">
              <div className="setting-info">
                <span className="setting-name">Data Refresh Rate</span>
                <span className="setting-description">
                  How often the UI re-renders chart ticks.
                </span>
              </div>
              <select
                className="neutral-select"
                value={uiSettings.refreshRate}
                onChange={(e) =>
                  setUiSettings({ ...uiSettings, refreshRate: e.target.value })
                }
              >
                <option value="500ms">Real-time (500ms)</option>
                <option value="1s">Standard (1s)</option>
                <option value="5s">Lazy (5s)</option>
              </select>
            </div>
          </div>

          <div className="divider-line"></div>

          {/* Category: System */}
          <div className="settings-category">
            <h3 className="category-label">Alerts & System</h3>

            <div className="setting-row">
              <div className="setting-info">
                <span className="setting-name">Push Notifications</span>
                <span className="setting-description">
                  Browser alerts for trade executions.
                </span>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={uiSettings.showNotifications}
                  onChange={() =>
                    setUiSettings({
                      ...uiSettings,
                      showNotifications: !uiSettings.showNotifications,
                    })
                  }
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-row">
              <div className="setting-info">
                <span className="setting-name">Performance Mode</span>
                <span className="setting-description">
                  Disable heavy CSS animations to save GPU.
                </span>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={!uiSettings.animations}
                  onChange={() =>
                    setUiSettings({
                      ...uiSettings,
                      animations: !uiSettings.animations,
                    })
                  }
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          <div className="settings-footer">
            <button className="neutral-btn grey-btn">Reset All</button>
            <button className="neutral-btn confirm-btn">Apply Locally</button>
          </div>
        </div>
      </div>

      {/* Persistence Notice */}
      <div className="control-bar">
        <div className="control-status">
          <div className="status-indicator highlight-silver-bg"></div>
          <span className="status-text silver-text">
            Storage: <strong>LocalStorage (Front)</strong>
          </span>
        </div>
      </div>
    </div>
  );
}
