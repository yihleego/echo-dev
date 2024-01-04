const {app, BrowserWindow, ipcMain} = require('electron')
const path = require('node:path')
const WebSocketServer = require('ws');
// Creating a new websocket server
const wss = new WebSocketServer.Server({port: 8080})

var clients = [];

// Creating connection using websocket
wss.on("connection", ws => {
    clients.push(ws)
    console.log("new client connected");

    // sending message to client
    //ws.send('Welcome, you are connected!');

    //on message from client
    ws.on("message", data => {
        console.log(`Client has sent us: ${data}`)
    });

    // handling what to do when clients disconnects from server
    ws.on("close", () => {
        console.log("the client has disconnected");
    });
    // handling client connection error
    ws.onerror = function () {
        console.log("Some Error occurred")
    }
});
console.log("The WebSocket server is running on port 8080");

function createWindow() {
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js')
        }
    })

    win.loadFile('index.html')
    return win
}

function createChildWindow() {
    const child = new BrowserWindow({
        // parent: win,
        transparent: true,
        frame: false,
        width: 9999,
        height: 9999,
        skipTaskbar: true,
        alwaysOnTop: true,
    })
    child.loadFile('child.html')
    child.setPosition(0, 0)
    //child.maximize();
    child.setIgnoreMouseEvents(true)
    child.show()
    child.on('close', e => {
        e.preventDefault();
    });
    return child
}

app.whenReady().then(() => {
    const win = createWindow()
    const child = createChildWindow()
    app.on('activate', () => {
        const allWindows = BrowserWindow.getAllWindows()
        if (allWindows.length === 0) {
            createWindow()
        } else if (allWindows.length === 1 && allWindows[0] === child) {
            createWindow()
        }
    })
    win.webContents.openDevTools({mode: 'detach'})
    //child.webContents.openDevTools({mode: 'detach'})

    ipcMain.handle('start', () => {
        console.log("start")
        for (let i in clients) {
            console.log("send to", i)
            clients[i].send('start');
        }
    })
    ipcMain.handle('stop', () => {
        console.log("stop")
        for (let i in clients) {
            console.log("send to", i)
            clients[i].send('stop');
        }
    })
})

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

