import { useEffect, useRef, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Topbar from "./components/layout/Topbar";
import Sidebar from "./components/layout/Sidebar";
import "./assets/App.css";

import api from "../api/axiosInstance.js";
import Home from "./pages/Navigation/Home";
import Resume from "./pages/Navigation/Resume";
import Setup from "./pages/Navigation/Setup";
import Positions from "./pages/Navigation/Positions";
import Graphs from "./pages/Navigation/Graphs";
import Backtesting from "./pages/Navigation/Backtesting";
import Log from "./pages/Navigation/Log";
import Api from "./pages/Management/Api";
import Docs from "./pages/Management/Docs";
import Settings from "./pages/Management/Settings";

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Topbar />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/Resume" element={<Resume />} />
            <Route path="/Setup" element={<Setup />} />
            <Route path="/Positions" element={<Positions />} />
            <Route path="/Graphs" element={<Graphs />} />
            <Route path="/Backtesting" element={<Backtesting />} />
            <Route path="/Log" element={<Log />} />
            <Route path="/Management/Api" element={<Api />} />
            <Route path="/Management/Docs" element={<Docs />} />
            <Route path="/Management/Settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
