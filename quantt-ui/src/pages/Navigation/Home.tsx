import React, { useState, useEffect } from "react";
import "../localassets/Home.css";

interface Trade {
  id: string;
  pair: string;
  type: "BUY" | "SELL";
  profit: number;
  time: string;
}

export default function Home() {
  const [status, setStatus] = useState<"Running" | "Paused" | "Stopped">(
    "Stopped",
  );
  const [pnl, setPnl] = useState({ net: 1250.45, today: 85.2, drawdown: 2.4 });
  const [marginUsage, setMarginUsage] = useState(35);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [stopConfirm, setStopConfirm] = useState(false);

  // Simulated Polling Logic
  useEffect(() => {
    const interval = setInterval(() => {
      console.log("Syncing with Bot...");
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  function handleAction(action: string) {
    if (action === "stop" && !stopConfirm) {
      setStopConfirm(true);
      setTimeout(() => setStopConfirm(false), 3000);
      return;
    }

    console.log(`Executing: POST /bot/${action}`);

    if (action === "start") setStatus("Running");
    if (action === "pause") setStatus("Paused");
    if (action === "stop") {
      setStatus("Stopped");
      setStopConfirm(false);
    }
  }

  return (
    <div className="container">
      {/* 1. TOP BAR: KILL SWITCH & STATUS */}
      <header className="topBar">
        <div className={`statusBadge ${status.toLowerCase()}`}>
          <span className="pulseDot"></span>
          {status}
        </div>

        <div className="buttonGroup">
          <button className="btnStart" onClick={() => handleAction("start")}>
            Start / Resume
          </button>

          <button className="btnPause" onClick={() => handleAction("pause")}>
            Pause
          </button>

          <button
            className={`btnStop ${stopConfirm ? "confirming" : ""}`}
            onClick={() => handleAction("stop")}
          >
            {stopConfirm ? "Confirm STOP?" : "Stop / Restart"}
          </button>
        </div>
      </header>

      {/* 2. MIDDLE SECTION: PERFORMANCE SNAPSHOT */}
      <section className="performanceGrid">
        <div className="card">
          <h3>Net Profit</h3>
          <p className={pnl.net >= 0 ? "positive" : "negative"}>
            ${pnl.net.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
        </div>
        <div className="card">
          <h3>Daily PnL</h3>
          <p className={pnl.today >= 0 ? "positive" : "negative"}>
            +${pnl.today.toLocaleString()}
          </p>
        </div>
        <div className="card">
          <h3>Max Drawdown</h3>
          <p className="warningText">{pnl.drawdown}%</p>
        </div>
      </section>

      {/* 3. BOTTOM SECTION: LIVE ACTIVITY FEED */}
      <section className="bottomSection">
        <div className="marginCard">
          <h3>Margin Health</h3>
          <div className="progressBarBg">
            <div
              className="progressBarFill"
              style={{
                width: `${marginUsage}%`,
                backgroundColor: marginUsage > 80 ? "#ff4d4d" : "#00e676",
              }}
            ></div>
          </div>
          <small>{marginUsage}% of risk limit utilized</small>
        </div>

        <div className="tradesWidget">
          <h3>Recent Trades (Last 5)</h3>
          <table className="tradeTable">
            <thead>
              <tr>
                <th>Pair</th>
                <th>Type</th>
                <th>Profit</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>ETH/USDT</td>
                <td>
                  <span className="buyTag">BUY</span>
                </td>
                <td className="positive">+$42.10</td>
                <td>18:45:22</td>
              </tr>
              <tr>
                <td>BTC/USDT</td>
                <td>
                  <span className="sellTag">SELL</span>
                </td>
                <td className="negative">-$12.05</td>
                <td>18:30:10</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
