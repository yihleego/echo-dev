import asyncio

from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
from websockets import server, WebSocketServerProtocol


def on_press(key):
    print(key)


def on_release(key):
    print(key)


def on_move(x, y):
    print('Mouse moved', x, y)


async def listenKeyboard():
    with KeyboardListener(on_press=on_press, on_release=on_release) as keyboard_listener:
        keyboard_listener.join()


async def listenMouse():
    with MouseListener(on_move=on_move) as mouse_listener:
        mouse_listener.join()


async def handle(websocket: WebSocketServerProtocol):
    print('connected', websocket.id, websocket.path)
    if websocket.path == '/browser':
        await handle_browser(websocket)
    elif websocket.path == '/client':
        await handle_client(websocket)
    else:
        await websocket.close()
    print('disconnected', websocket.id, websocket.path)


async def handle_client(websocket: WebSocketServerProtocol):
    async for message in websocket:
        print('handle_client message', websocket.id, websocket.path, message)
        await websocket.send(message)


async def handle_browser(websocket: WebSocketServerProtocol):
    async for message in websocket:
        print('handle_browser message', websocket.id, websocket.path, message)
        await websocket.send(message)


async def main():
    async with server.serve(handle, "localhost", 18000):
        await asyncio.Future()  # run forever
        # await asyncio.gather(listenKeyboard(), listenMouse())


if __name__ == '__main__':
    asyncio.run(main())
    print(1)
