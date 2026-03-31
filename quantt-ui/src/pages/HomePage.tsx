import React from "react";
import "./HomePage.css";

// ─────────────────────────────────────────────────────────────────────────────
// HomePage — skeleton layout for a financial broker dashboard
//
// Section map:
//   1. Page header      — title + date + CTA buttons
//   2. KPI strip        — 4 metric cards (portfolio value, P&L, margin, cash)
//   3. Chart area       — large primary chart (e.g. equity curve)
//   4. Positions table  — open positions list
//   5. Order book       — bid / ask columns
//   6. Watchlist        — compact ticker list
//   7. News feed        — headline cards
// ─────────────────────────────────────────────────────────────────────────────

const HomePage: React.FC = () => {
  return (
    <div className="home">

      {/* ── 1. Page header ─────────────────────────────────────────────────── */}
      <header className="home__header">
        <div className="home__header-left">
          <p className="label">Dashboard</p>
          <h1 className="home__title">Overview</h1>
        </div>
        <div className="home__header-right">
          {/* TODO: date / session info */}
          <div className="home__header-date" />
          {/* TODO: Quick-trade button */}
          <div className="home__header-cta home__header-cta--primary" />
          {/* TODO: Deposit button */}
          <div className="home__header-cta" />
        </div>
      </header>

      {/* ── 2. KPI strip ───────────────────────────────────────────────────── */}
      <section className="home__kpi-strip">
        {/* Portfolio total value */}
        <div className="card kpi-card">
          <div className="label">Portfolio Value</div>
          <div className="kpi-card__value" />
          <div className="kpi-card__delta" />
        </div>

        {/* Daily P&L */}
        <div className="card kpi-card">
          <div className="label">Today's P&L</div>
          <div className="kpi-card__value" />
          <div className="kpi-card__delta" />
        </div>

        {/* Buying power / margin */}
        <div className="card kpi-card">
          <div className="label">Buying Power</div>
          <div className="kpi-card__value" />
          <div className="kpi-card__bar">
            <div className="kpi-card__bar-fill" />
          </div>
        </div>

        {/* Cash balance */}
        <div className="card kpi-card">
          <div className="label">Cash Balance</div>
          <div className="kpi-card__value" />
          <div className="kpi-card__delta" />
        </div>
      </section>

      {/* ── 3 + 4 + 5. Middle row ──────────────────────────────────────────── */}
      <section className="home__middle">

        {/* 3. Primary chart */}
        <div className="card home__chart">
          {/* TODO: Chart toolbar — symbol selector, timeframe tabs */}
          <div className="home__chart-toolbar">
            <div className="home__chart-symbol" />
            <div className="home__chart-timeframes">
              {["1D","1W","1M","3M","1Y","ALL"].map(tf => (
                <div key={tf} className={`home__chart-tf ${tf === "1M" ? "home__chart-tf--active" : ""}`}>
                  {tf}
                </div>
              ))}
            </div>
          </div>

          {/* TODO: Charting library canvas (TradingView / Recharts / Victory) */}
          <div className="home__chart-canvas">
            <span className="home__chart-placeholder">
              chart canvas
            </span>
          </div>
        </div>

        {/* 5. Order book — right column */}
        <div className="card home__orderbook">
          <div className="label" style={{marginBottom: 12}}>Order Book</div>

          {/* Asks */}
          <div className="orderbook__side orderbook__side--asks">
            {/* TODO: render ask rows */}
            {Array.from({length: 7}).map((_, i) => (
              <div key={i} className="orderbook__row orderbook__row--ask">
                <div className="orderbook__price" />
                <div className="orderbook__size" />
                <div className="orderbook__bar" style={{width: `${90 - i*10}%`}} />
              </div>
            ))}
          </div>

          {/* Spread */}
          <div className="orderbook__spread">
            <span className="label">Spread</span>
            <div className="orderbook__spread-value" />
          </div>

          {/* Bids */}
          <div className="orderbook__side orderbook__side--bids">
            {Array.from({length: 7}).map((_, i) => (
              <div key={i} className="orderbook__row orderbook__row--bid">
                <div className="orderbook__price" />
                <div className="orderbook__size" />
                <div className="orderbook__bar" style={{width: `${40 + i*8}%`}} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── 4. Positions table ─────────────────────────────────────────────── */}
      <section className="card home__positions">
        <div className="home__positions-header">
          <div className="label">Open Positions</div>
          {/* TODO: filter / sort controls */}
          <div className="home__positions-controls" />
        </div>

        <table className="positions-table">
          <thead>
            <tr>
              {["Symbol","Side","Qty","Entry","Mark","P&L","P&L %","Actions"].map(col => (
                <th key={col} className="label">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {/* TODO: map over real positions data */}
            {Array.from({length: 5}).map((_, i) => (
              <tr key={i} className="positions-table__row">
                <td><div className="skel skel--short" /></td>
                <td><div className="skel skel--badge" /></td>
                <td><div className="skel skel--num" /></td>
                <td><div className="skel skel--num" /></td>
                <td><div className="skel skel--num" /></td>
                <td><div className="skel skel--num" /></td>
                <td><div className="skel skel--num" /></td>
                <td><div className="skel skel--actions" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* ── 6 + 7. Bottom row ──────────────────────────────────────────────── */}
      <section className="home__bottom">

        {/* 6. Watchlist */}
        <div className="card home__watchlist">
          <div className="home__watchlist-header">
            <div className="label">Watchlist</div>
            {/* TODO: add-ticker button */}
            <div className="home__watchlist-add" />
          </div>

          <div className="watchlist__list">
            {/* TODO: render ticker rows */}
            {Array.from({length: 8}).map((_, i) => (
              <div key={i} className="watchlist__row">
                <div className="watchlist__ticker">
                  <div className="skel skel--short" />
                  <div className="skel skel--tiny" />
                </div>
                <div className="watchlist__sparkline" />
                <div className="watchlist__price">
                  <div className="skel skel--num" />
                  <div className="skel skel--tiny" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 7. News feed */}
        <div className="card home__news">
          <div className="label" style={{marginBottom: 12}}>Market News</div>

          <div className="news__list">
            {/* TODO: render fetched news headlines */}
            {Array.from({length: 6}).map((_, i) => (
              <div key={i} className="news__item">
                <div className="news__meta">
                  <div className="skel skel--tag" />
                  <div className="skel skel--time" />
                </div>
                <div className="news__headline">
                  <div className="skel skel--line" />
                  <div className="skel skel--line skel--line-short" />
                </div>
              </div>
            ))}
          </div>
        </div>

      </section>
    </div>
  );
};

export default HomePage;
