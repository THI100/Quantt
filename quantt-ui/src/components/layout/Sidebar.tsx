import { useState } from "react";
import "../localassets/Sidebar.css";

interface NavLink {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const IconHome = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    <polyline points="9 22 9 12 15 12 15 22" />
  </svg>
);

// Resume — document with a person silhouette, like a CV
const IconResume = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <circle cx="10" cy="13" r="2" />
    <path d="M8 21v-1a2 2 0 0 1 4 0v1" />
    <line x1="15" y1="11" x2="18" y2="11" />
    <line x1="15" y1="15" x2="18" y2="15" />
  </svg>
);

// Setup — horizontal sliders representing configuration
const IconSetup = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="4"  y1="6"  x2="20" y2="6"  />
    <line x1="4"  y1="12" x2="20" y2="12" />
    <line x1="4"  y1="18" x2="20" y2="18" />
    <circle cx="8"  cy="6"  r="2" fill="currentColor" stroke="none" />
    <circle cx="15" cy="12" r="2" fill="currentColor" stroke="none" />
    <circle cx="10" cy="18" r="2" fill="currentColor" stroke="none" />
  </svg>
);

// Positions — stacked layers representing open trade positions
const IconPositions = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="14" width="20" height="6" rx="1" />
    <rect x="2" y="8"  width="20" height="6" rx="1" />
    <rect x="2" y="2"  width="20" height="6" rx="1" />
  </svg>
);

// Graphs — line chart with upward trend
const IconGraphs = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 17 8 11 13 14 21 5" />
    <line x1="3"  y1="21" x2="21" y2="21" />
    <line x1="3"  y1="5"  x2="3"  y2="21" />
  </svg>
);

// Backtesting — rewind arrow with a clock hand, symbolising replaying history
const IconBacktesting = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="1 4 1 10 7 10" />
    <path d="M3.51 15a9 9 0 1 0 .49-4.5" />
    <line x1="12" y1="7"  x2="12" y2="12" />
    <line x1="12" y1="12" x2="15" y2="14" />
  </svg>
);

// Log — bulleted list with dot markers, representing timestamped entries
const IconLog = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="9"  y1="6"  x2="20" y2="6"  />
    <line x1="9"  y1="12" x2="20" y2="12" />
    <line x1="9"  y1="18" x2="20" y2="18" />
    <circle cx="4" cy="6"  r="2" />
    <circle cx="4" cy="12" r="2" />
    <circle cx="4" cy="18" r="2" />
  </svg>
);

const IconUsers = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
    <circle cx="9" cy="7" r="4" />
    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </svg>
);

const IconDocs = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="16" y1="13" x2="8" y2="13" />
    <line x1="16" y1="17" x2="8" y2="17" />
    <polyline points="10 9 9 9 8 9" />
  </svg>
);

const IconSettings = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3" />
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14" />
    <path d="M12 2v2M12 20v2M2 12h2M20 12h2" />
  </svg>
);

const IconMenu = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="3" y1="12" x2="21" y2="12" />
    <line x1="3" y1="6"  x2="21" y2="6"  />
    <line x1="3" y1="18" x2="21" y2="18" />
  </svg>
);

const navLinks: NavLink[] = [
  // Main Navigation
  { label: "Home",        href: "/",            icon: <IconHome />        },
  { label: "Resume",      href: "/Resume",      icon: <IconResume />      },
  { label: "Setup",       href: "/Setup",       icon: <IconSetup />       },
  { label: "Positions",   href: "/Positions",   icon: <IconPositions />   },
  { label: "Graphs",      href: "/Graphs",      icon: <IconGraphs />      },
  { label: "Backtesting", href: "/Backtesting", icon: <IconBacktesting /> },
  { label: "Log",         href: "/Log",         icon: <IconLog />         },
  // Management
  { label: "Users",       href: "/users",       icon: <IconUsers />       },
  { label: "Docs",        href: "/docs",        icon: <IconDocs />        },
  { label: "Settings",    href: "/settings",    icon: <IconSettings />    },
];

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeLink, setActiveLink] = useState("/");

  return (
    <>
      <div className="sidebar-root">
        {/* Toggle Button */}
        <button
          className="sidebar-toggle"
          onClick={() => setIsOpen((prev) => !prev)}
          aria-expanded={isOpen}
          aria-label="Toggle navigation"
        >
          <IconMenu />
        </button>

        {/* Expandable Panel */}
        <nav
          className={`sidebar-panel${isOpen ? " open" : ""}`}
          aria-hidden={!isOpen}
        >
          <div className="sidebar-section-label">Navigation</div>

          {navLinks.slice(0, 7).map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={`sidebar-link${activeLink === link.href ? " active" : ""}`}
              onClick={(e) => {
                e.preventDefault();
                setActiveLink(link.href);
              }}
            >
              <span className="sidebar-link-icon">{link.icon}</span>
              {link.label}
            </a>
          ))}

          <div className="sidebar-divider" />
          <div className="sidebar-section-label">Management</div>

          {navLinks.slice(7).map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={`sidebar-link${activeLink === link.href ? " active" : ""}`}
              onClick={(e) => {
                e.preventDefault();
                setActiveLink(link.href);
              }}
            >
              <span className="sidebar-link-icon">{link.icon}</span>
              {link.label}
            </a>
          ))}

          <div className="sidebar-divider" />
        </nav>
      </div>
    </>
  );
}