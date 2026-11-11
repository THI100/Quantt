const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  // 1. Function to get the app version or system info
  getPlatform: () => process.platform,
  getCredentialEncryptionIdentity: () =>
    ipcRenderer.invoke("get-credential-encryption-identity"),

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

  // 4. Open external links in the default browser via the main process
  openLink: (url) => ipcRenderer.invoke("open-external-link", url),
});
