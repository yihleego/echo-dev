# -*- coding=utf-8
import asyncio
from enum import Enum
from functools import wraps

from pynput import mouse, keyboard

Key = keyboard.Key
Button = mouse.Button


class Event(str, Enum):
    KEYDOWN = "keydown"
    KEYUP = "keyup"
    CLICK = "click"
    DBCLICK = "dbclick"
    MOUSEDOWN = "mousedown"
    MOUSEUP = "mouseup"
    MOUSEMOVE = "mousemove"
    SCROLL = "scroll"


_keyboard_states: dict[Key, bool] = {}  # key -> pressed
_mouse_states: dict[Button, tuple[int, int]] = {}  # key -> position
_mouse_position: tuple[int, int] = (0, 0)
_registrations: dict[Event, list] = {
    Event.KEYDOWN: [],
    Event.KEYUP: [],
    Event.CLICK: [],
    Event.DBCLICK: [],
    Event.MOUSEDOWN: [],
    Event.MOUSEUP: [],
    Event.MOUSEMOVE: [],
    Event.SCROLL: [],
}


def _on_press(key):
    _keyboard_states[key] = True
    _trigger(Event.KEYDOWN, _mouse_position[0], _mouse_position[1], key)


def _on_release(key):
    _trigger(Event.KEYUP, _mouse_position[0], _mouse_position[1], key)
    _keyboard_states[key] = False


def _on_click(x, y, button, pressed):
    if pressed:
        _mouse_states[button] = (x, y)
        _trigger(Event.MOUSEDOWN, x, y, button)
    else:
        _trigger(Event.CLICK, x, y, button)
        _trigger(Event.MOUSEUP, x, y, button)
        _mouse_states[button] = None


def _on_move(x, y):
    global _mouse_position
    _mouse_position = (x, y)
    _trigger(Event.MOUSEMOVE, x, y)


def _on_scroll(x, y, dx, dy):
    global _mouse_position
    _mouse_position = (x, y)
    _trigger(Event.SCROLL, x, y, dx, dy)


def _trigger(event, *args):
    listeners = _registrations[event]
    for keys, func in listeners:
        ok = True
        if keys:
            for key in keys:
                if isinstance(key, Key):
                    if not _keyboard_states.get(key):
                        ok = False
                        break
                elif isinstance(key, Button):
                    if not _mouse_states.get(key):
                        ok = False
                        break
                else:
                    ok = False
                    break
        if ok:
            func(*args)


def _run():
    with keyboard.Listener(on_press=_on_press, on_release=_on_release) as k_listener, \
            mouse.Listener(on_click=_on_click, on_move=_on_move, on_scroll=_on_scroll) as m_listener:
        k_listener.join()
        m_listener.join()


def listen(event, keys, func):
    _registrations[event].append((keys, func))


async def main():
    _run()
    # threading.Thread(target=_run, daemon=True).start()


def listener(event, *keys):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        listen(event, keys, func)
        return wrapper

    return decorator


if __name__ == '__main__':
    @listener(Event.KEYDOWN)
    def on_keydown(x, y, key):
        print('on_keydown', x, y, key)


    @listener(Event.KEYUP)
    def on_keyup(x, y, key):
        print('on_keyup  ', x, y, key)


    @listener(Event.CLICK)
    def on_click(x, y, button):
        print('on_click    ', x, y, button)


    @listener(Event.MOUSEDOWN)
    def on_mousedown(x, y, button):
        print('on_mousedown', x, y, button)


    @listener(Event.MOUSEUP)
    def on_mouseup(x, y, button):
        print('on_mouseup  ', x, y, button)


    @listener(Event.MOUSEMOVE, Key.ctrl)
    def on_mousemove(x, y):
        print('on_mousemove', x, y)


    @listener(Event.SCROLL)
    def on_scroll(x, y, dx, dy):
        print('on_scroll', x, y, dx, dy)


    asyncio.run(main())
