import React from "react";
import "./TitleBar.css";

const TitleBar: React.FC = () => {
  const handleMinimize = () => window.electronAPI?.minimize();
  const handleMaximize = () => window.electronAPI?.maximize();
  const handleClose    = () => window.electronAPI?.close();

  return (
    <header className="titlebar">
      {/* Drag region covers the full bar */}
      <div className="titlebar__drag" />

      {/* Branding */}
      <div className="titlebar__brand">
        <span className="titlebar__logo">▲</span>
        <span className="titlebar__name">BROKER<em>APP</em></span>
      </div>

      {/* Status chip — placeholder */}
      <div className="titlebar__status">
        <span className="titlebar__status-dot" />
        <span>LIVE</span>
      </div>

      {/* Window controls */}
      <div className="titlebar__controls">
        <button onClick={handleMinimize} aria-label="Minimize">
          <svg viewBox="0 0 12 12" width="12" height="12"><rect y="5.5" width="12" height="1" fill="currentColor"/></svg>
        </button>
        <button onClick={handleMaximize} aria-label="Maximize">
          <svg viewBox="0 0 12 12" width="12" height="12"><rect x="1" y="1" width="10" height="10" rx="1" fill="none" stroke="currentColor" strokeWidth="1.2"/></svg>
        </button>
        <button onClick={handleClose} aria-label="Close" className="titlebar__close">
          <svg viewBox="0 0 12 12" width="12" height="12">
            <line x1="1" y1="1" x2="11" y2="11" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
            <line x1="11" y1="1" x2="1" y2="11" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
          </svg>
        </button>
      </div>
    </header>
  );
};

export default TitleBar;
