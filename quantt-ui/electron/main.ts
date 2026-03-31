import { app, BrowserWindow, ipcMain } from "electron";
import path from "path";

const isDev = process.env.NODE_ENV === "development" || !app.isPackaged;

function createWindow(): void {
  const win = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 680,
    frame: false,           // frameless — we render our own titlebar
    titleBarStyle: "hidden",
    backgroundColor: "#0a0c10",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
    show: false,            // avoid white flash on startup
  });

  // Load Vite dev-server in dev, built index.html in prod
  if (isDev) {
    win.loadURL("http://localhost:5173");
    win.webContents.openDevTools({ mode: "detach" });
  } else {
    win.loadFile(path.join(__dirname, "../dist/index.html"));
  }

  win.once("ready-to-show", () => win.show());
}

// ── Window control IPC handlers ──────────────────────────────────────────────
ipcMain.on("window:minimize", () =>
  BrowserWindow.getFocusedWindow()?.minimize()
);
ipcMain.on("window:maximize", () => {
  const win = BrowserWindow.getFocusedWindow();
  if (!win) return;
  win.isMaximized() ? win.unmaximize() : win.maximize();
});
ipcMain.on("window:close", () =>
  BrowserWindow.getFocusedWindow()?.close()
);

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
