import { contextBridge, ipcRenderer } from "electron";

// Expose a safe, typed API to the renderer process via window.electronAPI
contextBridge.exposeInMainWorld("electronAPI", {
  // Window controls
  minimize: () => ipcRenderer.send("window:minimize"),
  maximize: () => ipcRenderer.send("window:maximize"),
  close:    () => ipcRenderer.send("window:close"),

  // Platform info
  platform: process.platform,
});
