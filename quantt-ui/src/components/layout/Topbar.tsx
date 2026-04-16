import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../localassets/Topbar.css";
import Sidebar from "./Sidebar.tsx";
import api from "../../../api/axiosInstance.js";

// ─── Types ────────────────────────────────────────────────────────────────────

type BotStatus = "Online" | "Offline" | "Restarted" | "Error";

type ActiveExchange = "Bybit" | "Binance" | "Okx" | "None";

interface TopbarProps {
  botStatus?: BotStatus;
  activeExchange?: ActiveExchange;
}

// ─── Icons ────────────────────────────────────────────────────────────────────
// (Icons remain unchanged, omitted here for brevity)
const IconExchange = () => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <polyline points="17 1 21 5 17 9" />
    <path d="M3 11V9a4 4 0 0 1 4-4h14" />
    <polyline points="7 23 3 19 7 15" />
    <path d="M21 13v2a4 4 0 0 1-4 4H3" />
  </svg>
);
const IconApi = () => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
  </svg>
);
const IconClock = () => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
);
const IconBot = () => (
  <svg
    width="14"
    height="14"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <rect x="3" y="11" width="18" height="10" rx="2" />
    <circle cx="12" cy="5" r="2" />
    <line x1="12" y1="7" x2="12" y2="11" />
    <line x1="8" y1="15" x2="8" y2="17" />
    <line x1="16" y1="15" x2="16" y2="17" />
  </svg>
);

// ─── Helpers ─────────────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<
  BotStatus,
  { label: string; color: string; pulse: boolean }
> = {
  Online: { label: "Online", color: "#4ade80", pulse: true },
  Offline: { label: "Offline", color: "#f87171", pulse: false },
  Restarted: { label: "Restarted", color: "#60a5fa", pulse: true },
  Error: { label: "Error", color: "#ef4444", pulse: false },
  Connecting: { label: "Connecting", color: "#666", pulse: false },
};

function useTime() {
  const [time, setTime] = useState(() => new Date());
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return time;
}

const formatTime = (date: Date) =>
  date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
const formatDate = (date: Date) =>
  date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });

// ─── Component ───────────────────────────────────────────────────────────────

export default function Topbar({
  botStatus: initialBotStatus = "Connecting...",
  activeExchange: initialExchange = "Binance",
}: TopbarProps) {
  const [botStatus, setBotStatus] = useState<BotStatus>(initialBotStatus);
  const [activeExchange, setActiveExchange] =
    useState<ActiveExchange>(initialExchange);

  const now = useTime();

  const hasRun = useRef(false);

  const status =
    STATUS_CONFIG[botStatus as keyof typeof STATUS_CONFIG] ||
    STATUS_CONFIG.Connecting;

  const navigate = useNavigate();

  const onStatusClick = async () => {
    try {
      const response = await api.get<BotResponse>("/bot/status");
      const statusFromServer = response.data.status;

      console.log(statusFromServer);

      setBotStatus(statusFromServer);
    } catch (error: any) {
      console.error("Error Starting the bot:", error);

      setBotStatus("Error");
    }
  };

  const handleClick = () => {
    navigate("/Management/Api");
  };

  useEffect(() => {
    if (hasRun.current) return;

    onStatusClick();

    hasRun.current = true;
  }, []);

  return (
    <header className="topbar">
      <div className="topbar-section topbar-left">
        <Sidebar />

        <div className="topbar-divider" />

        <button
          className="topbar-status-btn"
          onClick={onStatusClick} // Use the prop here
          style={{ "--status-color": status.color } as React.CSSProperties}
        >
          <span className={`status-dot${status.pulse ? " pulse" : ""}`} />
          <IconBot />
          <span className="status-label">
            <strong>{status.label}</strong>
          </span>
        </button>
      </div>

      <div className="topbar-section topbar-center">
        <span className="topbar-brand">Quantt</span>
      </div>

      {/* ── Right: Exchange · API · Clock ── */}
      <div className="topbar-section topbar-right">
        <div className="topbar-pill" title="Active exchange">
          <IconExchange />
          <span>{activeExchange}</span>
        </div>

        <div className="topbar-divider" />

        <button
          className="topbar-api-btn"
          onClick={handleClick}
          title="API Management"
        >
          <IconApi />
          <span>API</span>
        </button>

        <div className="topbar-divider" />

        <div className="topbar-clock" title="Current time">
          <IconClock />
          <span className="clock-time">{formatTime(now)}</span>
          <span className="clock-date">{formatDate(now)}</span>
        </div>
      </div>
    </header>
  );
}
