import React from "react";
import TitleBar from "./components/TitleBar";
import Sidebar from "./components/Sidebar";
import HomePage from "./pages/HomePage";

const App: React.FC = () => {
  return (
    <div className="app-shell">
      {/* Custom frameless titlebar — draggable region */}
      <TitleBar />

      <div className="app-body">
        {/* Left navigation rail */}
        <Sidebar />

        {/* Main content area — pages render here */}
        <main className="app-main">
          <HomePage />
        </main>
      </div>
    </div>
  );
};

export default App;
