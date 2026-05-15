import { contextBridge, ipcRenderer, shell } from "electron";

contextBridge.exposeInMainWorld("electronAPI", {
  // 1. Function to get the app version or system info
  getPlatform: () => process.platform,

  // 2. Send a message to the Main process
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

  // 4. Open external links in the default browser
  openLink: (url) => shell.openExternal(url),
});
