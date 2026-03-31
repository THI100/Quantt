import React, { useState } from "react";
import "./Sidebar.css";

type NavItem = {
  id: string;
  label: string;
  icon: React.ReactNode;
};

const navItems: NavItem[] = [
  {
    id: "home",
    label: "Dashboard",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
        <rect x="2" y="2" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.4"/>
        <rect x="11" y="2" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.4"/>
        <rect x="2" y="11" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.4"/>
        <rect x="11" y="11" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.4"/>
      </svg>
    ),
  },
  {
    id: "markets",
    label: "Markets",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
        <polyline points="2,14 7,8 11,11 18,4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
        <polyline points="14,4 18,4 18,8" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
  },
  {
    id: "portfolio",
    label: "Portfolio",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
        <circle cx="10" cy="10" r="7.5" stroke="currentColor" strokeWidth="1.4"/>
        <path d="M10 10 L10 2.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
        <path d="M10 10 L16 14" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      </svg>
    ),
  },
  {
    id: "orders",
    label: "Orders",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
        <path d="M4 5h12M4 10h8M4 15h5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      </svg>
    ),
  },
  {
    id: "watchlist",
    label: "Watchlist",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
        <path d="M10 3.5C6 3.5 3 10 3 10s3 6.5 7 6.5 7-6.5 7-6.5-3-6.5-7-6.5z" stroke="currentColor" strokeWidth="1.4"/>
        <circle cx="10" cy="10" r="2" stroke="currentColor" strokeWidth="1.4"/>
      </svg>
    ),
  },
  {
    id: "news",
    label: "News",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
        <rect x="2.5" y="3.5" width="15" height="13" rx="1.5" stroke="currentColor" strokeWidth="1.4"/>
        <path d="M6 8h8M6 11h5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      </svg>
    ),
  },
];

const bottomItems: NavItem[] = [
  {
    id: "alerts",
    label: "Alerts",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
        <path d="M10 2.5a5.5 5.5 0 0 0-5.5 5.5v3L3 13h14l-1.5-2V8A5.5 5.5 0 0 0 10 2.5z" stroke="currentColor" strokeWidth="1.4"/>
        <path d="M8.5 16a1.5 1.5 0 0 0 3 0" stroke="currentColor" strokeWidth="1.4"/>
      </svg>
    ),
  },
  {
    id: "settings",
    label: "Settings",
    icon: (
      <svg viewBox="0 0 20 20" fill="none" width="18" height="18">
        <circle cx="10" cy="10" r="2" stroke="currentColor" strokeWidth="1.4"/>
        <path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.22 4.22l1.42 1.42M14.36 14.36l1.42 1.42M4.22 15.78l1.42-1.42M14.36 5.64l1.42-1.42" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      </svg>
    ),
  },
];

const Sidebar: React.FC = () => {
  const [active, setActive] = useState("home");

  return (
    <nav className="sidebar">
      <div className="sidebar__nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar__item ${active === item.id ? "sidebar__item--active" : ""}`}
            onClick={() => setActive(item.id)}
            title={item.label}
          >
            {item.icon}
            {active === item.id && <span className="sidebar__indicator" />}
          </button>
        ))}
      </div>

      <div className="sidebar__bottom">
        {bottomItems.map((item) => (
          <button
            key={item.id}
            className={`sidebar__item ${active === item.id ? "sidebar__item--active" : ""}`}
            onClick={() => setActive(item.id)}
            title={item.label}
          >
            {item.icon}
          </button>
        ))}

        {/* User avatar placeholder */}
        <div className="sidebar__avatar" title="Profile">
          <span>JD</span>
        </div>
      </div>
    </nav>
  );
};

export default Sidebar;
