import { contextBridge, ipcRenderer } from "electron";

// We use contextBridge to safely expose APIs to the React frontend
contextBridge.exposeInMainWorld("electronAPI", {
  // 1. A function to get the app version or system info
  getPlatform: () => process.platform,

  // 2. Send a message to the Main process (e.g., to open a folder)
  sendMessage: (channel, data) => {
    const validChannels = ["toMain"];
    if (validChannels.includes(channel)) {
      ipcRenderer.send(channel, data);
    }
  },

  // 3. Receive a message from the Main process
  onMessage: (channel, callback) => {
    const validChannels = ["fromMain"];
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (event, ...args) => callback(...args));
    }
  },
});
