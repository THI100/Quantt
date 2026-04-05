const { app, BrowserWindow } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

  const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      // Correctly points to your preload file
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, // Safety: strictly separates Node from React
      nodeIntegration: false, // Safety: prevents React from running Node scripts
    },
  });
}

  // If in dev mode, load the Vite dev server URL
  // If in production, load the built index.html
  win.loadURL(
    isDev
      ? 'http://localhost:5173'
      : `file://${path.join(__dirname, '../dist/index.html')}`
  );
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
