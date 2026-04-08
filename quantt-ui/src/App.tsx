import { BrowserRouter, Routes, Route } from "react-router-dom";
import Topbar from "./components/layout/Topbar";
import Sidebar from "./components/layout/Sidebar";
import "./assets/App.css";

import Home from "./pages/Home";
import Resume from "./pages/Resume";
import Setup from "./pages/Setup";
import Positions from "./pages/Positions";
import Graphs from "./pages/Graphs";
import Backtesting from "./pages/Backtesting";
import Log from "./pages/Log";

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Topbar />
        <main className="app-main">
          <div className="app-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/Resume" element={<Resume />} />
              <Route path="/Setup" element={<Setup />} />
              <Route path="/Positions" element={<Positions />} />
              <Route path="/Graphs" element={<Graphs />} />
              <Route path="/Backtesting" element={<Backtesting />} />
              <Route path="/Log" element={<Log />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
