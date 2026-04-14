// import React, { useState, useEffect } from "react";

// interface Trade {
//   id: string;
//   pair: string;
//   type: "BUY" | "SELL";
//   profit: number;
//   time: string;
// }

// export default function Home() {
//   const [status, setStatus] = useState<"Running" | "Paused" | "Stopped">(
//     "Stopped",
//   );
//   const [pnl, setPnl] = useState({ net: 1250.45, today: 85.2, drawdown: 2.4 });
//   const [marginUsage, setMarginUsage] = useState(35);
//   const [trades, setTrades] = useState<Trade[]>([]);
//   const [stopConfirm, setStopConfirm] = useState(false);

//   // Simulated Polling Logic
//   useEffect(() => {
//     const interval = setInterval(() => {
//       console.log("Syncing with Bot...");
//     }, 5000);
//     return () => clearInterval(interval);
//   }, []);

//   function handleAction(action: string) {
//     if (action === "stop" && !stopConfirm) {
//       setStopConfirm(true);
//       setTimeout(() => setStopConfirm(false), 3000);
//       return;
//     }

//     console.log(`Executing: POST /bot/${action}`);

//     if (action === "start") setStatus("Running");
//     if (action === "pause") setStatus("Paused");
//     if (action === "stop") {
//       setStatus("Stopped");
//       setStopConfirm(false);
//     }
//   }

//   return (
//     <div className="container">
//       {/* 1. TOP BAR: KILL SWITCH & STATUS */}
//       <header className="topBar">
//         <div className={`statusBadge ${status.toLowerCase()}`}>
//           <span className="pulseDot"></span>
//           {status}
//         </div>

//         <div className="buttonGroup">
//           <button className="btnStart" onClick={() => handleAction("start")}>
//             Start / Resume
//           </button>

//           <button className="btnPause" onClick={() => handleAction("pause")}>
//             Pause
//           </button>

//           <button
//             className={`btnStop ${stopConfirm ? "confirming" : ""}`}
//             onClick={() => handleAction("stop")}
//           >
//             {stopConfirm ? "Confirm STOP?" : "Stop / Restart"}
//           </button>
//         </div>
//       </header>

//       {/* 2. MIDDLE SECTION: PERFORMANCE SNAPSHOT */}
//       <section className="performanceGrid">
//         <div className="card">
//           <h3>Net Profit</h3>
//           <p className={pnl.net >= 0 ? "positive" : "negative"}>
//             ${pnl.net.toLocaleString(undefined, { minimumFractionDigits: 2 })}
//           </p>
//         </div>
//         <div className="card">
//           <h3>Daily PnL</h3>
//           <p className={pnl.today >= 0 ? "positive" : "negative"}>
//             +${pnl.today.toLocaleString()}
//           </p>
//         </div>
//         <div className="card">
//           <h3>Max Drawdown</h3>
//           <p className="warningText">{pnl.drawdown}%</p>
//         </div>
//       </section>

//       {/* 3. BOTTOM SECTION: LIVE ACTIVITY FEED */}
//       <section className="bottomSection">
//         <div className="marginCard">
//           <h3>Margin Health</h3>
//           <div className="progressBarBg">
//             <div
//               className="progressBarFill"
//               style={{
//                 width: `${marginUsage}%`,
//                 backgroundColor: marginUsage > 80 ? "#ff4d4d" : "#00e676",
//               }}
//             ></div>
//           </div>
//           <small>{marginUsage}% of risk limit utilized</small>
//         </div>

//         <div className="tradesWidget">
//           <h3>Recent Trades (Last 5)</h3>
//           <table className="tradeTable">
//             <thead>
//               <tr>
//                 <th>Pair</th>
//                 <th>Type</th>
//                 <th>Profit</th>
//                 <th>Time</th>
//               </tr>
//             </thead>
//             <tbody>
//               <tr>
//                 <td>ETH/USDT</td>
//                 <td>
//                   <span className="buyTag">BUY</span>
//                 </td>
//                 <td className="positive">+$42.10</td>
//                 <td>18:45:22</td>
//               </tr>
//               <tr>
//                 <td>BTC/USDT</td>
//                 <td>
//                   <span className="sellTag">SELL</span>
//                 </td>
//                 <td className="negative">-$12.05</td>
//                 <td>18:30:10</td>
//               </tr>
//             </tbody>
//           </table>
//         </div>
//       </section>
//     </div>
//   );
// }

import React, { useState, useEffect } from "react";
import "../localassets/Home.css";
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Shield,
  AlertTriangle,
} from "lucide-react";

interface Trade {
  id: string;
  coin: string;
  type: "BUY" | "SELL";
  price: number;
  profit: number;
  timestamp: Date;
}

interface Metrics {
  pnl: number;
  totalTrades: number;
  marginHealth: number;
  maxDrawdown: number;
}

type BotStatus = "online" | "offline" | "warning" | "error";

const Home: React.FC = () => {
  const [botStatus, setBotStatus] = useState<BotStatus>("offline");
  const [metrics, setMetrics] = useState<Metrics>({
    pnl: 2847.32,
    totalTrades: 1247,
    marginHealth: 78.5,
    maxDrawdown: -12.3,
  });

  const [recentTrades, setRecentTrades] = useState<Trade[]>([
    {
      id: "1",
      coin: "BTC/USDT",
      type: "BUY",
      price: 43250.5,
      profit: 125.8,
      timestamp: new Date(Date.now() - 1000 * 60 * 5),
    },
    {
      id: "2",
      coin: "ETH/USDT",
      type: "SELL",
      price: 2280.3,
      profit: -32.15,
      timestamp: new Date(Date.now() - 1000 * 60 * 12),
    },
    {
      id: "3",
      coin: "SOL/USDT",
      type: "BUY",
      price: 98.75,
      profit: 45.6,
      timestamp: new Date(Date.now() - 1000 * 60 * 18),
    },
    {
      id: "4",
      coin: "BNB/USDT",
      type: "SELL",
      price: 312.4,
      profit: 78.2,
      timestamp: new Date(Date.now() - 1000 * 60 * 25),
    },
    {
      id: "5",
      coin: "ADA/USDT",
      type: "BUY",
      price: 0.52,
      profit: -8.5,
      timestamp: new Date(Date.now() - 1000 * 60 * 33),
    },
  ]);

  const handleStart = () => {
    setBotStatus("online");
  };

  const handleRestart = () => {
    setBotStatus("warning");
    setTimeout(() => setBotStatus("online"), 2000);
  };

  const handleStop = () => {
    setBotStatus("offline");
  };

  const formatTime = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  const getStatusColor = (): string => {
    switch (botStatus) {
      case "online":
        return "#c8f04a";
      case "warning":
        return "#f0a04a";
      case "error":
        return "#f04a4a";
      default:
        return "#666";
    }
  };

  const getMarginHealthColor = (health: number): string => {
    if (health >= 70) return "#c8f04a";
    if (health >= 40) return "#f0a04a";
    return "#f04a4a";
  };

  return (
    <div className="home-container">
      {/* Dashboard Metrics */}
      <section className="dashboard-section">
        <div className="metrics-grid">
          {/* PnL Card */}
          <div className="metric-card pnl-card">
            <div className="metric-header">
              <span className="metric-label">Profit & Loss</span>
              {metrics.pnl >= 0 ? (
                <TrendingUp className="metric-icon positive" size={20} />
              ) : (
                <TrendingDown className="metric-icon negative" size={20} />
              )}
            </div>
            <div className="metric-value">
              <span className={metrics.pnl >= 0 ? "positive" : "negative"}>
                {metrics.pnl >= 0 ? "+" : ""}$
                {metrics.pnl.toLocaleString("en-US", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </span>
            </div>
            <div className="metric-subtext">Total unrealized</div>
          </div>

          {/* Total Trades Card */}
          <div className="metric-card">
            <div className="metric-header">
              <span className="metric-label">Total Trades</span>
              <Activity className="metric-icon" size={20} />
            </div>
            <div className="metric-value">
              <span>{metrics.totalTrades.toLocaleString()}</span>
            </div>
            <div className="metric-subtext">All-time executions</div>
          </div>

          {/* Margin Health Card */}
          <div className="metric-card margin-card">
            <div className="metric-header">
              <span className="metric-label">Margin Health</span>
              <Shield className="metric-icon" size={20} />
            </div>
            <div className="margin-bar-container">
              <div className="margin-bar-background">
                <div
                  className="margin-bar-fill"
                  style={{
                    width: `${metrics.marginHealth}%`,
                    background: getMarginHealthColor(metrics.marginHealth),
                  }}
                />
              </div>
              <div
                className="margin-percentage"
                style={{ color: getMarginHealthColor(metrics.marginHealth) }}
              >
                {metrics.marginHealth.toFixed(1)}%
              </div>
            </div>
            <div className="metric-subtext">Collateral ratio</div>
          </div>

          {/* Max Drawdown Card */}
          <div className="metric-card drawdown-card">
            <div className="metric-header">
              <span className="metric-label">Max Drawdown</span>
              <AlertTriangle className="metric-icon warning" size={20} />
            </div>
            <div className="metric-value">
              <span className="negative">
                {metrics.maxDrawdown.toFixed(1)}%
              </span>
            </div>
            <div className="metric-subtext">Peak to trough</div>
          </div>
        </div>
      </section>

      {/* Activity Feed */}
      <section className="activity-section">
        <div className="section-header">
          <h2 className="section-title">Recent Activity</h2>
          <span className="activity-count">{recentTrades.length} trades</span>
        </div>

        <div className="activity-feed">
          {recentTrades.map((trade) => (
            <div key={trade.id} className="trade-item">
              <div className="trade-left">
                <div className={`trade-type ${trade.type.toLowerCase()}`}>
                  {trade.type}
                </div>
                <div className="trade-coin">{trade.coin}</div>
              </div>

              <div className="trade-middle">
                <div className="trade-price">
                  $
                  {trade.price.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                  })}
                </div>
              </div>

              <div className="trade-right">
                <div
                  className={`trade-profit ${trade.profit >= 0 ? "positive" : "negative"}`}
                >
                  {trade.profit >= 0 ? "+" : ""}$
                  {Math.abs(trade.profit).toFixed(2)}
                </div>
                <div className="trade-time">{formatTime(trade.timestamp)}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom Control Bar */}
      <div className="control-bar">
        <div className="control-status">
          <div
            className={`status-indicator ${botStatus === "online" ? "pulse" : ""}`}
            style={{ background: getStatusColor() }}
          />
          <span className="status-text" style={{ color: getStatusColor() }}>
            Bot Status: <strong>{botStatus.toUpperCase()}</strong>
          </span>
        </div>

        <div className="control-actions">
          <button
            className="control-btn start-btn"
            onClick={handleStart}
            disabled={botStatus === "online"}
          >
            Start
          </button>
          <button
            className="control-btn restart-btn"
            onClick={handleRestart}
            disabled={botStatus === "offline"}
          >
            Restart
          </button>
          <button
            className="control-btn stop-btn"
            onClick={handleStop}
            disabled={botStatus === "offline"}
          >
            Stop
          </button>
        </div>
      </div>
    </div>
  );
};

export default Home;
