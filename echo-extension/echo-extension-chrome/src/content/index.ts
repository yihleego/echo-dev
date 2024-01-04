import Inspector from './Inspector';

let inspector: Inspector;

async function initialize(): Promise<void> {
  const {default: Inspector} = await import('./Inspector');
  inspector = new Inspector();
  console.log('create inspector', inspector)
}

async function activateInspector(): Promise<void> {
  console.log('activateInspector');
  if (!inspector) {
    await initialize();
  }
  await inspector.activate();
}

function deactivateInspector(): void {
  console.log('deactivateInspector');
  if (inspector) {
    inspector.deactivate();
  }
}

function deactivateNotification(): void {
  console.log('deactivateNotification');
}

function activateNotification(): void {
  console.log('activateNotification');
}

chrome.runtime.onMessage.addListener(async (request, sender, sendResponse) => {
  if (request.action === 'activateInspector') {
    await activateInspector();
  } else if (request.action === 'deactivateInspector') {
    deactivateInspector();
  } else if (request.action === 'activateNotification') {
    activateNotification();
  } else if (request.action === 'deactivateNotification') {
    deactivateNotification();
  }
});
