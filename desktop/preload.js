const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('desktop', { quitAsk: () => ipcRenderer.send('quit-ask') });
