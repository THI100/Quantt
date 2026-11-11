import { app, BrowserWindow, ipcMain, shell } from "electron";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";
import os from "node:os";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let pyProc = null;
let viteProc = null;
const engineDir = path.resolve(__dirname, "../../quantt-engine");
const viteUrl = "http://localhost:5173";

function findDevelopmentPython() {
  if (process.env.QUANTT_PYTHON_EXECUTABLE) {
    return process.env.QUANTT_PYTHON_EXECUTABLE;
  }

  const candidates =
    process.platform === "win32"
      ? [
          path.join(engineDir, ".venv", "Scripts", "python.exe"),
          path.join(engineDir, "venv", "Scripts", "python.exe"),
        ]
      : [
          path.join(engineDir, ".venv", "bin", "python"),
          path.join(engineDir, "venv", "bin", "python"),
        ];

  return candidates.find((candidate) => fs.existsSync(candidate)) ?? "python";
}

async function waitForVite() {
  const deadline = Date.now() + 30_000;

  while (Date.now() < deadline) {
    if (viteProc?.exitCode !== null && viteProc?.exitCode !== undefined) {
      throw new Error(`Vite exited before becoming ready (code ${viteProc.exitCode}).`);
    }

    try {
      const response = await fetch(viteUrl, { signal: AbortSignal.timeout(1_000) });
      if (response.ok) return;
    } catch {
      // Vite is still starting; retry until it responds or the startup deadline expires.
    }

    await new Promise((resolve) => setTimeout(resolve, 300));
  }

  throw new Error(`Vite did not become available at ${viteUrl} within 30 seconds.`);
}

async function startDevelopmentVite() {
  try {
    const response = await fetch(viteUrl, { signal: AbortSignal.timeout(1_000) });
    if (response.ok) {
      console.log("Using existing Vite dev server.");
      return;
    }
  } catch {
    // Start Vite below when no development server is already listening.
  }

  const viteExecutable = path.join(
    __dirname,
    "../node_modules/.bin",
    process.platform === "win32" ? "vite.cmd" : "vite",
  );
  viteProc = spawn(viteExecutable, ["--host", "127.0.0.1", "--strictPort"], {
    cwd: path.resolve(__dirname, ".."),
    shell: process.platform === "win32",
    stdio: ["ignore", "pipe", "pipe"],
  });

  viteProc.stdout.on("data", (data) => console.log(`[Vite stdout]: ${data}`));
  viteProc.stderr.on("data", (data) => console.error(`[Vite stderr]: ${data}`));
  viteProc.on("error", (error) => {
    console.error("[Electron error] Failed to start Vite:", error);
  });

  console.log("Started Vite dev server.");
  await waitForVite();
}

ipcMain.handle("get-credential-encryption-identity", () => ({
  username: process.env.USERNAME || process.env.USER || "",
  ipv6Addresses: Object.values(os.networkInterfaces())
    .flatMap((addresses) => addresses ?? [])
    .filter((address) => address.family === "IPv6" && !address.internal)
    .map((address) => address.address.split("%")[0]),
}));

ipcMain.handle("open-external-link", (_event, url) => shell.openExternal(url));

function startPythonBackend() {
  let pyBinaryPath;

  if (process.env.QUANTT_ENGINE_EXECUTABLE) {
    pyBinaryPath = process.env.QUANTT_ENGINE_EXECUTABLE;
    pyProc = spawn(pyBinaryPath);
    console.log("Spawned configured Python executable.");
  } else if (!app.isPackaged) {
    // 1. In Development: Run your local python entry script
    // Adjust this path to wherever your backend main.py lives relative to main.js
    const mainPath = path.join(engineDir, "main.py");
    pyBinaryPath = findDevelopmentPython();
    pyProc = spawn(pyBinaryPath, [mainPath], { cwd: engineDir });
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

  win.webContents.on("console-message", (event) => {
    if (event.level === "error") {
      console.error(`[Renderer error] ${event.message}`);
    }
  });
  win.webContents.on("render-process-gone", (_event, details) => {
    console.error(`[Electron error] Renderer exited: ${details.reason}`);
  });
  win.webContents.on("did-fail-load", (_event, code, description, url) => {
    console.error(
      `[Electron error] Failed to load ${url}: ${description} (${code})`,
    );
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
app.whenReady().then(async () => {
  if (!app.isPackaged && !process.env.QUANTT_TEST_MODE) {
    await startDevelopmentVite();
  }
  startPythonBackend();
  createWindow();
}).catch((error) => {
  console.error("[Electron error] Application startup failed:", error);
  viteProc?.kill();
  pyProc?.kill();
  app.exit(1);
});

// Kill backend when the app closes
app.on("window-all-closed", () => {
  if (pyProc !== null) {
    pyProc.kill();
    console.log("Killed Python sidecar process.");
  }
  if (viteProc !== null) {
    viteProc.kill();
    console.log("Stopped Vite dev server.");
  }
  if (process.platform !== "darwin") app.quit();
});
