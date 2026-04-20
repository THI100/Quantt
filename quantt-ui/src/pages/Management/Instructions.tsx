import "../localassets/Instructions.css";

export default function Instructions() {
  return (
    <div className="home-container">
      <div className="section-header">
        <h2 className="section-title silver-text">System Documentation</h2>
        <span className="activity-count">Rev: 0.9.5-BETA</span>
      </div>

      <div className="docs-wrapper">
        {/* Sidebar Navigation */}
        <nav className="docs-sidebar">
          <div className="sidebar-group">
            <span className="group-label">Quick Start</span>
            <a href="#setup" className="nav-item active">
              Core Setup
            </a>
            <a href="#api" className="nav-item">
              API Integration
            </a>
          </div>
          <div className="sidebar-group">
            <span className="group-label">Trading Engine</span>
            <a href="#risk" className="nav-item">
              Risk Management
            </a>
            <a href="#signals" className="nav-item">
              Signal Analysis
            </a>
          </div>
        </nav>

        {/* Content Area */}
        <main className="docs-content">
          <section id="setup" className="doc-section">
            <h3 className="doc-h3">01. Informations</h3>
            <p className="doc-p">
              This app is in a version of pre-release, meaning this software may
              not have the full capacity it was designed to have, may have bugs
              and "glitches" on a few pages or metrics.
            </p>
            <p className="doc-p">
              As you may have noticed, some pages are empty or features are
              inexistent, those are still on development, and might appear on
              the next versions, such as 0.2, 0.3 ... some of the features that
              are coming by are
              <b> backtesting, log, AI powered features, and others... </b>
            </p>
            <p className="doc-p">
              Follow the Instructions below for more informations on how to
              continue, setup and make usage of this bot.
            </p>
          </section>

          <section id="init" className="doc-section">
            <h3 className="doc-h3">02. Initialization</h3>
            <p className="doc-p">
              <div className="info-callout highlight-blue-bg">
                <span className="callout-icon">ℹ</span>
                <p>
                  Pro-Tip II: Ensure the backend/engine is online and running on
                  localhost:8000.
                </p>
              </div>
              <li>
                Initialize as dev or make usage of the .exe programs, located on
                the dist folder.
              </li>
              <li>
                Set up your API and share your key and secret on the API page by
                clicking on the sidebar. For more information follow section 3.
              </li>
              <li>Select the Setup page by clicking on the sidebar.</li>
              <li>
                Insert your configurations for trading and risk, there will be
                some initial values.
              </li>
              <li>
                Now go to Home page and click on the start button and relax...
              </li>
            </p>
            <div className="info-callout highlight-blue-bg">
              <span className="callout-icon">ℹ</span>
              <p>
                Pro-Tip I: Ensure your system clock is synchronized with UTC
                time for accurate trade execution.
              </p>
            </div>
          </section>

          <section id="api" className="doc-section">
            <h3 className="doc-h3">03. API Permissions</h3>
            <p className="doc-p">
              Following for more instructions, for the api setup, you will need
              to ensure you have an API key and API secret, besides the exchange
              you want to use. Insert and send them to the backend, now it
              should all work normal.
            </p>
          </section>

          {/*<section id="risk" className="doc-section">
            <h3 className="doc-h3">04. Understanding Drawdown</h3>
            <p className="doc-p">
              Sed ut perspiciatis unde omnis iste natus error sit voluptatem
              accusantium doloremque laudantium, totam rem aperiam, eaque ipsa
              quae ab illo inventore veritatis et quasi architecto beatae vitae
              dicta sunt explicabo.
            </p>
          </section>*/}
        </main>
      </div>

      {/* Bottom Actions */}
      <div className="control-bar">
        <div className="control-status">
          <div className="status-indicator highlight-silver-bg"></div>
          <span className="status-text silver-text">
            Reading Mode: <strong>Default</strong>
          </span>
        </div>
        {/*<div className="control-actions">
          <button className="control-btn grey-btn">Print Manual</button>
          <button className="control-btn start-btn">Contact Support</button>
        </div>*/}
      </div>
    </div>
  );
}
