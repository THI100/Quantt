import { useCallback, useEffect, useState } from "react";
import "../localassets/Setup.css";
import api from "../../../api/axiosInstance.js";

type TradingConfig = {
  name: string;
  is_demo_enabled: boolean;
  timeframe: string;
  exchange: string;
  execution_order: string;
  future_spot: string;
  list_of_interest: string[];
  list_of_parameters: string[];
};

type RiskConfig = {
  name: string;
  risk_reward_ratio: number;
  acceptable_confidence: number;
  atr_multiplier: number;
  maximum_loss: number;
  percentage_of_capital_per_trade: number;
  leverage: number;
  maximum_iceberg_share: number;
  cross_isolated: string;
};

const emptyTrading: TradingConfig = {
  name: "base",
  is_demo_enabled: false,
  timeframe: "",
  exchange: "",
  execution_order: "",
  future_spot: "",
  list_of_interest: [],
  list_of_parameters: [],
};
const emptyRisk: RiskConfig = {
  name: "base",
  risk_reward_ratio: 0,
  acceptable_confidence: 0,
  atr_multiplier: 0,
  maximum_loss: 0,
  percentage_of_capital_per_trade: 0,
  leverage: 1,
  maximum_iceberg_share: 0,
  cross_isolated: "",
};

export default function Setup() {
  const [trading, setTrading] = useState<TradingConfig>(emptyTrading);
  const [risk, setRisk] = useState<RiskConfig>(emptyRisk);
  const [tradingProfiles, setTradingProfiles] = useState<string[]>([]);
  const [riskProfiles, setRiskProfiles] = useState<string[]>([]);
  const [selectedTradingProfile, setSelectedTradingProfile] = useState("base");
  const [selectedRiskProfile, setSelectedRiskProfile] = useState("base");
  const [deleteTradingProfile, setDeleteTradingProfile] = useState("");
  const [deleteRiskProfile, setDeleteRiskProfile] = useState("");
  const [message, setMessage] = useState("");

  const refreshProfiles = useCallback(async () => {
    const [tradingRes, riskRes] = await Promise.all([
      api.get<string[]>("/config/trading/profiles"),
      api.get<string[]>("/config/risk/profiles"),
    ]);
    setTradingProfiles(tradingRes.data);
    setRiskProfiles(riskRes.data);
    setDeleteTradingProfile((current) => current || tradingRes.data[0] || "");
    setDeleteRiskProfile((current) => current || riskRes.data[0] || "");
    return { trading: tradingRes.data, risk: riskRes.data };
  }, []);

  const loadProfile = async (mode: "trading" | "risk", profile: string) => {
    if (!profile) return;
    try {
      const { data } = await api.get(`/config/${mode}`, {
        params: { profile_name: profile },
      });
      if (mode === "trading") {
        setTrading(data);
        setSelectedTradingProfile(profile);
      } else {
        setRisk(data);
        setSelectedRiskProfile(profile);
      }
    } catch (error) {
      console.error(`Error loading ${mode} profile:`, error);
      setMessage(`Could not load ${mode} profile.`);
    }
  };

  useEffect(() => {
    refreshProfiles()
      .then(async (profiles) => {
        const tradingProfile = profiles.trading.includes("base")
          ? "base"
          : profiles.trading[0];
        const riskProfile = profiles.risk.includes("base")
          ? "base"
          : profiles.risk[0];
        if (tradingProfile) await loadProfile("trading", tradingProfile);
        if (riskProfile) await loadProfile("risk", riskProfile);
      })
      .catch((error) => console.error("Error loading profiles:", error));
  }, [refreshProfiles]);

  const saveProfile = async (mode: "trading" | "risk", create: boolean) => {
    try {
      const config = mode === "trading" ? trading : risk;
      const profile = config.name.trim();
      if (!profile) {
        setMessage(`Enter a name for the ${mode} profile.`);
        return;
      }
      const selectedProfile =
        mode === "trading" ? selectedTradingProfile : selectedRiskProfile;
      if (!create && profile !== selectedProfile) {
        setMessage(
          "Profile names cannot be changed when saving edits. Use Create Profile to save under a new name.",
        );
        return;
      }
      const payload = { ...config, name: profile };
      if (create) {
        await api.put(`/config/${mode}`, payload);
      } else {
        await api.patch(`/config/${mode}`, payload, {
          params: { profile_name: selectedProfile },
        });
      }
      if (mode === "trading") setSelectedTradingProfile(profile);
      else setSelectedRiskProfile(profile);
      await refreshProfiles();
      setMessage(`${mode === "trading" ? "Trading" : "Risk"} profile saved.`);
    } catch (error) {
      console.error(`Failed to save ${mode} profile:`, error);
      setMessage(`Failed to save ${mode} profile.`);
    }
  };

  const deleteProfile = async (mode: "trading" | "risk") => {
    const profile =
      mode === "trading" ? deleteTradingProfile : deleteRiskProfile;
    if (!profile) return;
    try {
      await api.delete(`/config/${mode}/${encodeURIComponent(profile)}`);
      await refreshProfiles();
      const remaining =
        mode === "trading"
          ? tradingProfiles.filter((p) => p !== profile)
          : riskProfiles.filter((p) => p !== profile);
      if (mode === "trading") {
        const next = remaining[0] || "";
        setDeleteTradingProfile(next);
        if (selectedTradingProfile === profile) {
          setTrading(emptyTrading);
          setSelectedTradingProfile(next);
          if (next) await loadProfile("trading", next);
        }
      } else {
        const next = remaining[0] || "";
        setDeleteRiskProfile(next);
        if (selectedRiskProfile === profile) {
          setRisk(emptyRisk);
          setSelectedRiskProfile(next);
          if (next) await loadProfile("risk", next);
        }
      }
      setMessage(`${mode} profile deleted.`);
    } catch (error) {
      console.error(`Failed to delete ${mode} profile:`, error);
      setMessage(`Failed to delete ${mode} profile.`);
    }
  };

  const handleCheckboxChange = (param: string) => {
    const updatedList = trading.list_of_parameters.includes(param)
      ? trading.list_of_parameters.filter((p) => p !== param)
      : [...trading.list_of_parameters, param];
    setTrading({ ...trading, list_of_parameters: updatedList });
  };

  return (
    <div className="home-container">
      <div className="section-header">
        <h2 className="section-title">System Configuration</h2>
        <span className="activity-count">v0.1.0-set</span>
      </div>

      <div className="setup-grid">
        <div className="config-panel highlight-blue-border">
          <div className="panel-header">
            <span className="panel-icon blue-text">◈</span>
            <h3>Trading Engine</h3>
          </div>
          <form className="setup-form" onSubmit={(e) => e.preventDefault()}>
            <div className="profile-controls">
              <div className="input-group">
                <label htmlFor="trading-profile">Trading profile</label>
                <select
                  id="trading-profile"
                  className="terminal-input"
                  value={selectedTradingProfile}
                  onChange={(e) => loadProfile("trading", e.target.value)}
                >
                  {tradingProfiles.map((profile) => (
                    <option key={profile} value={profile}>
                      {profile}
                    </option>
                  ))}
                </select>
              </div>
              <div className="input-group">
                <label htmlFor="trading-name">Profile name</label>
                <input
                  id="trading-name"
                  className="terminal-input"
                  value={trading.name}
                  onChange={(e) =>
                    setTrading({ ...trading, name: e.target.value })
                  }
                />
              </div>
            </div>
            <div className="input-group">
              <label>Execution Mode</label>
              <div className="toggle-wrapper">
                <input
                  type="checkbox"
                  checked={trading.is_demo_enabled}
                  onChange={(e) => {
                    const enabled = e.target.checked;
                    setTrading({
                      ...trading,
                      is_demo_enabled: enabled,
                      ...(enabled && trading.exchange === "mexc"
                        ? { exchange: "binance" }
                        : {}),
                    });
                  }}
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
            <div className="input-row">
              <div className="input-group">
                <label>Exchange</label>
                <select
                  value={trading.exchange}
                  className="terminal-input"
                  onChange={(e) =>
                    setTrading({
                      ...trading,
                      exchange: e.target.value,
                      ...(e.target.value === "mexc"
                        ? { is_demo_enabled: false }
                        : {}),
                    })
                  }
                >
                  <option value="binance">Binance</option>
                  <option value="bybit">Bybit</option>
                  <option value="okx">OKX</option>
                  <option value="mexc" disabled={trading.is_demo_enabled}>
                    Mexc
                  </option>
                  <option value="aster">Aster</option>
                  <option value="dydx">DYDX</option>
                  <option value="hyperliquid">HyperLiquid</option>
                  <option value="lighter">Lighter</option>
                </select>
              </div>
              <div className="input-group">
                <label>Execution Mode</label>
                <select
                  value={trading.execution_order}
                  className="terminal-input"
                  onChange={(e) =>
                    setTrading({ ...trading, execution_order: e.target.value })
                  }
                >
                  <option value="market">Market</option>
                  <option value="limit">Limit</option>
                </select>
              </div>
            </div>
            <div className="input-group">
              <label>Assets (Comma separated)</label>
              <textarea
                className="terminal-input"
                value={trading.list_of_interest.join(", ")}
                onChange={(e) =>
                  setTrading({
                    ...trading,
                    list_of_interest: e.target.value
                      .split(",")
                      .map((x) => x.trim())
                      .filter(Boolean),
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
            <div className="profile-actions">
              <button
                type="button"
                className="control-btn restart-btn"
                onClick={() => saveProfile("trading", false)}
              >
                Save Changes
              </button>
              <button
                type="button"
                className="control-btn restart-btn"
                onClick={() => saveProfile("trading", true)}
              >
                Create Profile
              </button>
            </div>
            <div className="profile-delete">
              <div className="input-group">
                <label>Delete trading profile</label>
                <select
                  className="terminal-input"
                  value={deleteTradingProfile}
                  onChange={(e) => setDeleteTradingProfile(e.target.value)}
                >
                  {tradingProfiles.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>
              <button
                type="button"
                className="control-btn stop-btn"
                disabled={!deleteTradingProfile}
                onClick={() => deleteProfile("trading")}
              >
                Delete
              </button>
            </div>
          </form>
        </div>

        <div className="config-panel highlight-purple-border">
          <div className="panel-header">
            <span className="panel-icon purple-text">🛡</span>
            <h3>Risk Parameters</h3>
          </div>
          <form className="setup-form" onSubmit={(e) => e.preventDefault()}>
            <div className="profile-controls">
              <div className="input-group">
                <label htmlFor="risk-profile">Risk profile</label>
                <select
                  id="risk-profile"
                  className="terminal-input"
                  value={selectedRiskProfile}
                  onChange={(e) => loadProfile("risk", e.target.value)}
                >
                  {riskProfiles.map((profile) => (
                    <option key={profile} value={profile}>
                      {profile}
                    </option>
                  ))}
                </select>
              </div>
              <div className="input-group">
                <label htmlFor="risk-name">Profile name</label>
                <input
                  id="risk-name"
                  className="terminal-input"
                  value={risk.name}
                  onChange={(e) => setRisk({ ...risk, name: e.target.value })}
                />
              </div>
            </div>
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
                    setRisk({
                      ...risk,
                      risk_reward_ratio: Number(e.target.value),
                    })
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
                    setRisk({ ...risk, leverage: Number(e.target.value) })
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
                    setRisk({ ...risk, maximum_loss: Number(e.target.value) })
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
                  setRisk({
                    ...risk,
                    acceptable_confidence: Number(e.target.value),
                  })
                }
              />
            </div>
            <div className="input-row">
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
                      percentage_of_capital_per_trade: Number(e.target.value),
                    })
                  }
                />
              </div>
              <div className="input-group">
                <label htmlFor="maximum-iceberg-share">
                  Maximum Iceberg Share (decimal, limit: 0.1)
                </label>
                <input
                  id="maximum-iceberg-share"
                  type="number"
                  step="0.01"
                  value={risk.maximum_iceberg_share}
                  className="terminal-input"
                  onChange={(e) =>
                    setRisk({
                      ...risk,
                      maximum_iceberg_share: Number(e.target.value),
                    })
                  }
                />
              </div>
            </div>
            <div className="profile-actions">
              <button
                type="button"
                className="control-btn start-btn"
                onClick={() => saveProfile("risk", false)}
              >
                Save Changes
              </button>
              <button
                type="button"
                className="control-btn start-btn"
                onClick={() => saveProfile("risk", true)}
              >
                Create Profile
              </button>
            </div>
            <div className="profile-delete">
              <div className="input-group">
                <label>Delete risk profile</label>
                <select
                  className="terminal-input"
                  value={deleteRiskProfile}
                  onChange={(e) => setDeleteRiskProfile(e.target.value)}
                >
                  {riskProfiles.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>
              <button
                type="button"
                className="control-btn stop-btn"
                disabled={!deleteRiskProfile}
                onClick={() => deleteProfile("risk")}
              >
                Delete
              </button>
            </div>
          </form>
        </div>
      </div>
      {message && (
        <p className="setup-message" role="status">
          {message}
        </p>
      )}
    </div>
  );
}
