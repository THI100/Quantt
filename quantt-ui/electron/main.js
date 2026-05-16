import { app, BrowserWindow } from "electron";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let pyProc = null;

function startPythonBackend() {
  let pyBinaryPath;

  if (!app.isPackaged) {
    // 1. In Development: Run your local python entry script
    // Adjust this path to wherever your backend main.py lives relative to main.js
    pyBinaryPath = path.join(__dirname, "../backend/main.py");
    pyProc = spawn("python", [pyBinaryPath]);
    console.log("Spawned development Python process.");
  } else {
    // 2. In Production: Run the compiled binary bundled inside Electron's extraResources
    pyBinaryPath = path.join(
      process.resourcesPath,
      "backend-dist",
      "main",
      "QuanttEngine",
    );
    if (process.platform === "win32") {
      pyBinaryPath += ".exe";
    }
    console.log("Backend exists:", fs.existsSync(pyBinaryPath));
    pyProc = spawn(pyBinaryPath);
    console.log("Spawned production Python executable.");
  }

  // Log Python outputs to Electron terminal for debugging
  pyProc.stdout.on("data", (data) => console.log(`[Python stdout]: ${data}`));
  pyProc.stderr.on("data", (data) => console.error(`[Python stderr]: ${data}`));

  pyProc.on("close", (code) => {
    console.log(`Python process exited with code ${code}`);
  });
}

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    icon: path.join(__dirname, "../build/qi.png"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (app.isPackaged) {
    const indexPath = path.join(
      app.getAppPath(),
      "dist",
      "index.html"
    );

    console.log("Loading production frontend:", indexPath);

    win.loadFile(indexPath);
  } else {
    console.log("Loading Vite dev server...");
    win.loadURL("http://localhost:5173");
  }
}

// Start Backend and open the window
app.whenReady().then(() => {
  startPythonBackend();
  createWindow();
});

// Kill backend when the app closes
app.on("window-all-closed", () => {
  if (pyProc !== null) {
    pyProc.kill();
    console.log("Killed Python sidecar process.");
  }
  if (process.platform !== "darwin") app.quit();
});
