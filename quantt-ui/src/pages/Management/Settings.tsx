import { useRef } from "react";
import "../localassets/Settings.css";
import { useBotStore, selectUI } from "../../store/botStore";

export default function Settings() {
  const ui = useBotStore(selectUI);
  const { setUISettings, resetAll, exportJSON, importJSON } = useBotStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Export settings as a downloaded .json file ──────────────────────────
  const handleExport = () => {
    const blob = new Blob([exportJSON()], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "store.json";
    a.click();
    URL.revokeObjectURL(url);
  };

  // ── Import settings from a .json file ───────────────────────────────────
  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      if (typeof ev.target?.result === "string") {
        importJSON(ev.target.result);
      }
    };
    reader.readAsText(file);
    // reset so the same file can be re-imported if needed
    e.target.value = "";
  };

  return (
    <div className="home-container">
      <div className="section-header">
        <h2 className="section-title silver-text">Local Preferences</h2>
        <span className="activity-count">Global Store</span>
      </div>

      <div className="settings-wrapper">
        <div className="settings-card">
          {/* ── Display & Interface ───────────────────────────────────── */}
          <div className="settings-category">
            <h3 className="category-label">Display & Interface</h3>

            <div className="setting-row">
              <div className="setting-info">
                <span className="setting-name">Dark Mode</span>
                <span className="setting-description">
                  Change the main color only
                </span>
              </div>
              <label className="switch">
                <input
                  type="checkbox"
                  checked={ui.darkMode}
                  onChange={() => setUISettings({ darkMode: !ui.darkMode })}
                />
                <span className="slider"></span>
              </label>
            </div>

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
                  checked={ui.compactMode}
                  onChange={() =>
                    setUISettings({ compactMode: !ui.compactMode })
                  }
                />
                <span className="slider"></span>
              </label>
            </div>

            <div className="setting-row">
              <div className="setting-info">
                <label htmlFor="refresh-rate" className="setting-name">
                  Data Refresh Rate
                </label>
                <span className="setting-description">
                  How often the UI re-renders chart ticks.
                </span>
              </div>
              <select
                id="refresh-rate"
                className="neutral-select"
                value={ui.refreshRate}
                onChange={(e) =>
                  setUISettings({
                    refreshRate: e.target.value as "500ms" | "1s" | "5s",
                  })
                }
              >
                <option value="500ms">Real-time (500ms)</option>
                <option value="1s">Standard (1s)</option>
                <option value="5s">Lazy (5s)</option>
              </select>
            </div>
          </div>

          <div className="divider-line"></div>

          {/* ── Alerts & System ───────────────────────────────────────── */}
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
                  checked={ui.showNotifications}
                  onChange={() =>
                    setUISettings({
                      showNotifications: !ui.showNotifications,
                    })
                  }
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          <div className="settings-footer">
            <button className="neutral-btn grey-btn" onClick={resetAll}>
              Reset All
            </button>
            <button className="neutral-btn grey-btn" onClick={handleExport}>
              Export JSON
            </button>
            <button
              className="neutral-btn grey-btn"
              onClick={() => fileInputRef.current?.click()}
            >
              Import JSON
            </button>
            {/* hidden file input for import */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              style={{ display: "none" }}
              onChange={handleImport}
            />
          </div>
        </div>
      </div>

      {/* ── Persistence notice ──────────────────────────────────────────── */}
      <div className="control-bar">
        <div className="control-status">
          <div className="status-indicator highlight-silver-bg"></div>
          <span className="status-text silver-text">
            Storage: <strong>Zustand → LocalStorage (bot-settings)</strong>
          </span>
        </div>
      </div>
    </div>
  );
}
