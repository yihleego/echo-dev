interface TabStates {
  [key: number]: string;
}

/*class WebSocketFactory {
  private ws!: WebSocket

  constructor() {
  }

  public getWebSocket(): WebSocket {
    return this.ws;
  } vb
}*/


function connect() {
  const ws = new WebSocket('ws://localhost:8080');
  const tabStates: TabStates = {};
  let recording = false
  ws.onopen = function () {
    console.error('Socket is connected!');

    /*ws.send(JSON.stringify({
    }));*/
    chrome.action.setBadgeText({
      text: 'ON'
    });
    /*    chrome.action.getUserSettings()
          .then(settings => {
            const host = settings['host']
            const port = settings['port']
          })*/
    chrome.tabs.onActivated.addListener(async activeInfo => {
      const tabId = activeInfo.tabId;
      if (!tabId) return;
      tabStates[tabId] = 'ON';

      if (recording) {
        console.error('onActivated:', tabId);
        if (!tabId) return;
        await chrome.tabs.sendMessage(tabId, {
          action: 'activateInspector'
        });
        await chrome.tabs.sendMessage(tabId, {
          action: 'activateNotification'
        });
      } else {
        await chrome.tabs.sendMessage(tabId, {
          action: 'deactivateInspector'
        });
        await chrome.tabs.sendMessage(tabId, {
          action: 'deactivateNotification'
        });
      }

    });

    chrome.tabs.onRemoved.addListener(async (tabId, removeInfo) => {
      delete tabStates[tabId];
      chrome.action.setBadgeText({
        text: 'OFF'
      });
    });

  };

  ws.onmessage = function (e) {
    console.error('Message:', e.data);
    if (e.data === 'start') {
      recording = true
    } else {
      recording = false
    }
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      for (let i in tabs) {
        const tabId = tabs[i].id;
        if (!tabId) return;
        if (recording) {
          console.error('onActivated:', tabId);
          chrome.tabs.sendMessage(tabId, {
            action: 'activateInspector'
          });
          chrome.tabs.sendMessage(tabId, {
            action: 'activateNotification'
          });
        } else {
          chrome.tabs.sendMessage(tabId, {
            action: 'deactivateInspector'
          });
          chrome.tabs.sendMessage(tabId, {
            action: 'deactivateNotification'
          });
        }
      }
    });
  };

  ws.onclose = function (e) {
    console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
    chrome.action.setBadgeText({
      text: 'OFF'
    });
    setTimeout(function () {
      connect();
    }, 1000);
  };

  ws.onerror = function (err) {
    console.error('Socket encountered error: ', err, 'Closing socket');
    ws.close();
  };
}

connect();

/*const tabStates: TabStates = {};

chrome.runtime.onInstalled.addListener(() => {
  /!*chrome.action.setBadgeText({
    text: 'OFF'
  });*!/
});

chrome.action.onClicked.addListener(async tab => {
  const tabId: number | undefined = tab.id;
  if (!tabId) return;
  const prevState = tabStates[tabId] || 'OFF';
  const nextState = prevState === 'ON' ? 'OFF' : 'ON';

  tabStates[tabId] = nextState;

  await chrome.action.setBadgeText({
    tabId: tabId,
    text: nextState
  });

  if (nextState === 'ON') {
    await chrome.tabs.sendMessage(tabId, {
      action: 'activateInspector'
    });
    await chrome.tabs.sendMessage(tabId, {
      action: 'activateNotification'
    });
  } else if (nextState === 'OFF') {
    await chrome.tabs.sendMessage(tabId, {
      action: 'deactivateInspector'
    });
    await chrome.tabs.sendMessage(tabId, {
      action: 'deactivateNotification'
    });
  }
});

chrome.tabs.onActivated.addListener(async activeInfo => {
  const tabId = activeInfo.tabId;
  const state = tabStates[tabId] || 'OFF';

  /!*await chrome.action.setBadgeText({
    tabId: tabId,
    text: state
  });*!/
});

chrome.tabs.onRemoved.addListener(async (tabId, removeInfo) => {
  delete tabStates[tabId];
});*/

export {}
