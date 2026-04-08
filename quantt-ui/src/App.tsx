import Topbar from "./components/layout/Topbar"
import Sidebar from "./components/layout/Sidebar"
import "./App.css"

function App() {

  return (
    <>
      <div className="app-layout">
        <Sidebar />
        <Topbar />
      </div>
      <div className="main-content">
        {/* Main content goes here */}
      </div>
    </>
  )
}

export default App
