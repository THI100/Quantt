import { app, BrowserWindow, ipcMain } from "electron";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import os from "node:os";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let pyProc = null;

ipcMain.handle("get-credential-encryption-identity", () => ({
  username: process.env.USERNAME || process.env.USER || "",
  ipv6Addresses: Object.values(os.networkInterfaces())
    .flatMap((addresses) => addresses ?? [])
    .filter((address) => address.family === "IPv6" && !address.internal)
    .map((address) => address.address.split("%")[0]),
}));

function startPythonBackend() {
  let pyBinaryPath;

  if (process.env.QUANTT_ENGINE_EXECUTABLE) {
    pyBinaryPath = process.env.QUANTT_ENGINE_EXECUTABLE;
    pyProc = spawn(pyBinaryPath);
    console.log("Spawned configured Python executable.");
  } else if (!app.isPackaged) {
    // 1. In Development: Run your local python entry script
    // Adjust this path to wherever your backend main.py lives relative to main.js
    pyBinaryPath = path.join(__dirname, "../quantt-engine/main.py");
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
  pyProc.on("error", (error) => {
    console.error("[Electron error] Failed to start Python backend:", error);
  });

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

  win.webContents.on("console-message", (_event, details) => {
    if (details.level === 2) {
      console.error(`[Renderer error] ${details.message}`);
    }
  });
  win.webContents.on("render-process-gone", (_event, details) => {
    console.error(`[Electron error] Renderer exited: ${details.reason}`);
  });
  win.webContents.on("did-fail-load", (_event, code, description, url) => {
    console.error(`[Electron error] Failed to load ${url}: ${description} (${code})`);
  });

  if (app.isPackaged || process.env.QUANTT_TEST_MODE) {
    const indexPath = path.join(app.getAppPath(), "dist", "index.html");

    console.log("Loading production frontend:", indexPath);

    win.loadFile(indexPath);
  } else {
    console.log("Loading Vite dev server...");
    win.loadURL("http://localhost:5173");
  }
}

process.on("uncaughtException", (error) => {
  console.error("[Electron error] Uncaught exception:", error);
  app.exit(1);
});

process.on("unhandledRejection", (reason) => {
  console.error("[Electron error] Unhandled rejection:", reason);
  app.exit(1);
});

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
