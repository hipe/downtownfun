const { app, BrowserWindow } = require('electron');

const { PythonShell } = require('python-shell');

const path = require('path');

const _options = {
  args: ['aa', 'bb', 'cc'],
  scriptPath: path.resolve(path.join(__dirname, '..')),
  pythonPath: 'python3',  // ..
  pythonOptions: ['-u'],  // stdin, stdout & stderr unbuffered
  mode: 'text'
};

const pyshell = new PythonShell('../backend.py', _options);

// pyshell.send('some user data')

pyshell.on('message', (message) => {
  console.log('receceived message: ' + message);
})

pyshell.end((err, code, signal) => {
  if (err) throw err;
  console.log('the exit code was: ' + code);
  console.log('the exit signal was ' + signal);
  console.log('finished with thing.');
});



// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow;

function createWindow () {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true
    }
  });

  // and load the index.html of the app.
  mainWindow.loadFile('src/index.html');

  // Open the DevTools.
  mainWindow.webContents.openDevTools();

  // Emitted when the window is closed.
  mainWindow.on('closed', () => {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null
  });
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow);

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) {
    createWindow();
  }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
/*
# #born.
*/
