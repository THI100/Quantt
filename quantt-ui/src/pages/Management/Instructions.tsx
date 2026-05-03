import "../localassets/Instructions.css";

export default function Instructions() {
  return (
    <div className="home-container">
      <div className="section-header">
        <h2 className="section-title silver-text">System Documentation</h2>
        <span className="activity-count">Rev: 0.1.0-set</span>
      </div>

      <div className="docs-wrapper">
        {/* Sidebar Navigation */}
        <nav className="docs-sidebar">
          <div className="sidebar-group">
            <span className="group-label">Quick Start</span>
            <a href="#overview" className="nav-item active">
              Overview
            </a>
            <a href="#setup" className="nav-item">
              Getting Started
            </a>
            <a href="#api" className="nav-item">
              API Key Setup
            </a>
          </div>
          <div className="sidebar-group">
            <span className="group-label">Trading Engine</span>
            <a href="#risk" className="nav-item">
              Risk Management
            </a>
            <a href="#signals" className="nav-item">
              Signal & Strategy
            </a>
          </div>
          <div className="sidebar-group">
            <span className="group-label">Other</span>
            <a href="#backtesting" className="nav-item">
              Backtesting
            </a>
            <a href="#faq" className="nav-item">
              Troubleshooting / FAQ
            </a>
          </div>
        </nav>

        {/* Content Area */}
        <main className="docs-content">
          {/* ── 01. Overview ── */}
          <section id="overview" className="doc-section">
            <h3 className="doc-h3">01. Overview</h3>
            <p className="doc-p">
              Welcome to the trading bot documentation. This software is
              currently in pre-release (<strong>v0.1.0-set</strong>), meaning
              certain features may be incomplete, hidden, or subject to change
              between versions. Some pages may be empty — this is expected.
            </p>
            <p className="doc-p">
              Upcoming features include <strong>backtesting</strong>, an
              activity log, AI-powered signal analysis, and extended exchange
              coverage. These will roll out progressively in versions 1.0+.
            </p>
            <p className="doc-p">
              The system is composed of two parts: a <strong>frontend</strong>{" "}
              (this interface) and a <strong>backend engine</strong> that runs
              locally and handles all trade execution, signal processing, and
              risk enforcement. Both must be running simultaneously for the bot
              to operate.
            </p>
          </section>

          {/* ── 02. Getting Started ── */}
          <section id="setup" className="doc-section">
            <h3 className="doc-h3">02. Getting Started</h3>
            <p className="doc-p">
              Follow the steps below to get the system up and running for the
              first time.
            </p>

            <div className="info-callout highlight-blue-bg">
              <span className="callout-icon">ℹ</span>
              <p>
                The backend engine must be running on{" "}
                <strong>localhost:8000</strong> before you interact with any
                page. Without it, all API calls from the frontend will fail
                silently.
              </p>
            </div>

            <ol className="doc-ol">
              <li className="doc-li">
                <strong>Start the backend.</strong> Either run the project in
                dev mode via your terminal, or launch the pre-built{" "}
                <code>.exe</code> located in the <code>/dist</code> folder. Wait
                until the console confirms the engine is online.
              </li>
              <li className="doc-li">
                <strong>Open this interface.</strong> Launch the frontend the
                same way — dev mode or the corresponding <code>.exe</code>. You
                should see the dashboard load without errors.
              </li>
              <li className="doc-li">
                <strong>Configure your API keys.</strong> Navigate to the{" "}
                <strong>API</strong> page from the sidebar and insert your
                exchange credentials. See section 03 for full details.
              </li>
              <li className="doc-li">
                <strong>Configure trading parameters.</strong> Go to the{" "}
                <strong>Setup</strong> page and fill in your risk and strategy
                settings. Default values are pre-filled as a starting reference.
              </li>
              <li className="doc-li">
                <strong>Start the bot.</strong> Head to the{" "}
                <strong>Home</strong> page and click the <strong>Start</strong>{" "}
                button. The engine will begin monitoring the market and
                executing trades based on your configuration.
              </li>
            </ol>

            <div className="info-callout highlight-blue-bg">
              <span className="callout-icon">ℹ</span>
              <p>
                Ensure your system clock is synchronized with{" "}
                <strong>UTC</strong>. Time drift can cause missed signals or
                incorrect order timing. On Windows, check{" "}
                <em>Settings → Time & Language → Sync now</em>.
              </p>
            </div>
          </section>

          {/* ── 03. API Key Setup ── */}
          <section id="api" className="doc-section">
            <h3 className="doc-h3">03. API Key Setup</h3>
            <p className="doc-p">
              The bot currently supports <strong>Binance</strong> as its primary
              exchange, with additional support for <strong>Bybit</strong>,{" "}
              <strong>OKX</strong>, and <strong>MEXC</strong> available in the
              backend. Select your exchange on the API page and provide the
              corresponding credentials.
            </p>

            <p className="doc-p">To generate an API key on your exchange:</p>
            <ol className="doc-ol">
              <li className="doc-li">
                Log in to your exchange account and navigate to the API
                management section (usually under account settings or security).
              </li>
              <li className="doc-li">
                Create a new API key. Give it a recognizable label such as{" "}
                <em>"TradingBot"</em>.
              </li>
              <li className="doc-li">
                Enable the following permissions: <strong>Read</strong> and{" "}
                <strong>Spot/Futures Trading</strong>. Do <strong>not</strong>{" "}
                enable withdrawal permissions — the bot does not require them
                and enabling them is a security risk.
              </li>
              <li className="doc-li">
                Copy your <strong>API Key</strong> and{" "}
                <strong>API Secret</strong>. The secret is only shown once —
                store it securely.
              </li>
              <li className="doc-li">
                Paste both values into the respective fields on the{" "}
                <strong>API</strong> page of this interface and click{" "}
                <strong>Save / Send</strong>. The backend will validate the
                credentials and confirm the connection.
              </li>
            </ol>

            <div className="info-callout highlight-blue-bg">
              <span className="callout-icon">ℹ</span>
              <p>
                If you are using <strong>Binance</strong>, consider restricting
                the API key to your IP address for an added layer of security.
                This option is available during key creation on the Binance
                dashboard.
              </p>
            </div>
          </section>

          {/* ── 04. Risk Management ── */}
          <section id="risk" className="doc-section">
            <h3 className="doc-h3">04. Risk Management</h3>
            <p className="doc-p">
              Risk controls are configured on the <strong>Setup</strong> page.
              These parameters are enforced by the backend engine before any
              order is placed. Understanding each one is essential to running
              the bot safely.
            </p>

            <p className="doc-p">
              <strong>Stop Loss (SL) & Take Profit (TP)</strong>
            </p>
            <p className="doc-p">
              Set as a percentage relative to the entry price. The engine
              automatically places SL and TP orders immediately after a position
              is opened. Example: an SL of <code>2%</code> and TP of{" "}
              <code>4%</code> gives a 1:2 risk/reward ratio per trade.
            </p>

            <p className="doc-p">
              <strong>Max Drawdown Limit</strong>
            </p>
            <p className="doc-p">
              Defines the maximum cumulative loss (as a percentage of the
              starting balance) the bot is allowed to reach before it halts all
              trading activity. Once this threshold is hit, the bot stops and
              requires a manual restart. Use this to protect your account from
              runaway losses during adverse market conditions.
            </p>

            <p className="doc-p">
              <strong>Position Size & Leverage</strong>
            </p>
            <p className="doc-p">
              Position size determines how much of your available balance is
              allocated per trade (e.g. <code>5%</code> per position). Leverage
              multiplies your exposure — use with caution. Higher leverage
              increases both potential gains and potential losses. For most
              users, keeping leverage between <code>1x</code> and{" "}
              <code>5x</code> is recommended.
            </p>

            <p className="doc-p">
              <strong>Daily Loss Limit</strong>
            </p>
            <p className="doc-p">
              Caps the total loss the bot can incur within a single UTC day.
              Once the limit is reached, no new trades will be opened until the
              next day resets the counter. This is independent of the max
              drawdown limit and acts as a short-term safety net.
            </p>

            <div className="info-callout highlight-blue-bg">
              <span className="callout-icon">ℹ</span>
              <p>
                All risk fields have default values pre-filled. Review and
                adjust them to match your risk tolerance before starting the bot
                for the first time.
              </p>
            </div>
          </section>

          {/* ── 05. Signal & Strategy Config ── */}
          <section id="signals" className="doc-section">
            <h3 className="doc-h3">05. Signal & Strategy Config</h3>
            <p className="doc-p">
              The bot uses a signal-based approach to determine when to enter
              and exit positions. Signals are generated by the backend engine
              based on market data and your configured strategy parameters.
            </p>

            <p className="doc-p">
              <strong>Selecting a Strategy</strong>
            </p>
            <p className="doc-p">
              On the <strong>Setup</strong> page, choose the strategy you want
              the bot to run. Each strategy has its own set of configurable
              parameters that will appear once selected.
            </p>

            <p className="doc-p">
              <strong>Trading Pair & Timeframe</strong>
            </p>
            <p className="doc-p">
              Define which market pair the bot will trade (e.g.{" "}
              <code>BTC/USDT</code>) and the candle timeframe it should analyze
              (e.g. <code>15m</code>, <code>1h</code>, <code>4h</code>). Shorter
              timeframes generate more signals with higher noise; longer
              timeframes generate fewer but generally more reliable signals.
            </p>

            <p className="doc-p">
              <strong>Signal Confirmation</strong>
            </p>
            <p className="doc-p">
              Some strategies support optional confirmation filters — for
              example, requiring multiple indicators to agree before entering a
              trade. These reduce the number of trades but improve signal
              quality. Check the Setup page for available toggles on your
              selected strategy.
            </p>

            <div className="info-callout highlight-blue-bg">
              <span className="callout-icon">ℹ</span>
              <p>
                Strategy parameters take effect immediately on save — you do not
                need to restart the bot. However, any open position will
                continue under the previous parameters until it is closed.
              </p>
            </div>
          </section>

          {/* ── 06. Backtesting ── */}
          <section id="backtesting" className="doc-section">
            <h3 className="doc-h3">06. Backtesting</h3>
            <p className="doc-p">
              Backtesting is currently <strong>under development</strong> and
              will be available in a future release. When live, it will allow
              you to simulate your strategy against historical market data
              before running it with real funds.
            </p>
            <div className="info-callout highlight-blue-bg">
              <span className="callout-icon">ℹ</span>
              <p>
                This feature is planned for an upcoming version. Keep an eye on
                the revision number in the top-right corner for updates.
              </p>
            </div>
          </section>

          {/* ── 07. Troubleshooting / FAQ ── */}
          <section id="faq" className="doc-section">
            <h3 className="doc-h3">07. Troubleshooting / FAQ</h3>

            <p className="doc-p">
              <strong>The dashboard loads but shows no data.</strong>
            </p>
            <p className="doc-p">
              The backend engine is likely not running. Make sure the engine
              process is active on <code>localhost:8000</code> before opening
              the frontend. Check your terminal or task manager for the process.
            </p>

            <p className="doc-p">
              <strong>My API key is rejected.</strong>
            </p>
            <p className="doc-p">
              Double-check that you copied both the key and secret without extra
              spaces. Confirm that the correct exchange is selected. Also verify
              that the key has <em>Spot/Futures Trading</em> permissions enabled
              on your exchange account.
            </p>

            <p className="doc-p">
              <strong>The bot opened a trade but ignored my Stop Loss.</strong>
            </p>
            <p className="doc-p">
              Ensure your SL value is set and saved before starting the bot. SL
              orders are placed at the moment of entry — if the engine was
              started without a valid SL value, no protective order will have
              been placed. Stop the bot, verify your risk settings, and restart.
            </p>

            <p className="doc-p">
              <strong>The bot stopped trading unexpectedly.</strong>
            </p>
            <p className="doc-p">
              This is likely the Max Drawdown or Daily Loss Limit being
              triggered. Check the dashboard for any active alerts or status
              messages. If a limit was hit, review your risk configuration
              before restarting.
            </p>

            <p className="doc-p">
              <strong>Some pages are blank or features are missing.</strong>
            </p>
            <p className="doc-p">
              This is expected in the current BETA version. Features such as the
              activity log, backtesting, and AI-powered analysis are still in
              development and will appear in future releases.
            </p>

            <p className="doc-p">
              <strong>Trades are executing at the wrong time.</strong>
            </p>
            <p className="doc-p">
              Verify that your system clock is synced to UTC. Time drift — even
              by a few seconds — can affect candle close detection and order
              timing. On Windows: <em>Settings → Time & Language → Sync now</em>
              .
            </p>
          </section>
        </main>
      </div>

      {/* Bottom Bar */}
      <div className="control-bar">
        <div className="control-status">
          <div className="status-indicator highlight-silver-bg"></div>
          <span className="status-text silver-text">
            Reading Mode: <strong>Default</strong>
          </span>
        </div>
      </div>
    </div>
  );
}
