const { app, BrowserWindow, Menu, globalShortcut, dialog, ipcMain } = require('electron');
const path = require('path');

app.commandLine.appendSwitch('ignore-gpu-blocklist');
app.commandLine.appendSwitch('enable-gpu-rasterization');
app.commandLine.appendSwitch('force_high_performance_gpu');
app.setAppUserModelId('com.helmetsoft.hanoi');

let win;
function create() {
  Menu.setApplicationMenu(null);
  win = new BrowserWindow({
    width: 1400, height: 860, minWidth: 720, minHeight: 480,
    backgroundColor: '#05060a', show: false, title: 'Hanoi Tornyai RT',
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: { preload: path.join(__dirname, 'preload.js'), backgroundThrottling: true, spellcheck: false }
  });
  win.once('ready-to-show', () => { win.maximize(); win.show(); });
  win.webContents.on('before-input-event', (e, input) => {
    if (input.type === 'keyDown' && input.key === 'F11') { win.setFullScreen(!win.isFullScreen()); e.preventDefault(); }
  });
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  win.loadFile(path.join(__dirname, 'game', 'index.html'));
}
ipcMain.on('quit-ask', async () => {
  if (win.isFullScreen()) { win.setFullScreen(false); return; }
  const r = await dialog.showMessageBox(win, { type: 'question', buttons: ['Kilépés', 'Mégse'], defaultId: 1, cancelId: 1, title: 'Hanoi Tornyai RT', message: 'Kilépsz a játékból?' });
  if (r.response === 0) app.quit();
});
app.whenReady().then(create);
app.on('window-all-closed', () => app.quit());
