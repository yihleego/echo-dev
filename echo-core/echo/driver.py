# -*- coding: utf-8 -*-
# Copyright (c) 2024 Echo Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import time
from abc import ABC, abstractmethod
from typing import Callable

from PIL import Image

from .utils import win32, screenshot


class Driver(ABC):
    def __init__(self, handle: int, process_id: int = None, process_name: str = None,
                 window_name: str = None, class_name: str = None):
        self._handle = handle
        if not process_id:
            process_id = win32.get_process_id_from_handle(handle)
        if not process_name:
            process_name = win32.get_process_name_by_process_id(process_id)
        if not window_name:
            window_name = win32.get_window_text(handle)
        if not class_name:
            class_name = win32.get_class_name(handle)
        self._process_id = process_id
        self._process_name = process_name
        self._window_name = window_name
        self._class_name = class_name

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def process_id(self) -> int:
        return self._process_id

    @property
    def process_name(self) -> str:
        return self._process_name

    @property
    def window_name(self) -> str:
        return self._window_name

    @property
    def class_name(self) -> str:
        return self._class_name

    @property
    def rectangle(self) -> tuple[int, int, int, int]:
        raise win32.get_window_rect(self.handle)

    def screenshot(self, filename: str = None) -> Image:
        self.set_foreground()
        time.sleep(0.06)
        return screenshot(self.rectangle, filename)

    def set_foreground(self) -> bool:
        self.show()
        return win32.set_foreground(self.handle, self.process_id)

    def move(self, x: int = None, y: int = None, width: int = None, height: int = None, repaint=True) -> bool:
        return win32.move_window(self.handle, self.process_id, x, y, width, height, repaint)

    def hide(self) -> bool:
        return win32.show_window(self.handle, win32.SW_HIDE)

    def show(self) -> bool:
        return win32.show_window(self.handle, win32.SW_SHOW)

    def maximize(self) -> bool:
        return win32.show_window(self.handle, win32.SW_MAXIMIZE)

    def minimize(self) -> bool:
        return win32.show_window(self.handle, win32.SW_MINIMIZE)

    def restore(self) -> bool:
        return win32.show_window(self.handle, win32.SW_RESTORE)

    def is_minimized(self) -> bool:
        return win32.get_window_placement(self.handle).showCmd == win32.SW_SHOWMINIMIZED

    def is_maximized(self) -> bool:
        return win32.get_window_placement(self.handle).showCmd == win32.SW_SHOWMAXIMIZED

    def is_normal(self) -> bool:
        return win32.get_window_placement(self.handle).showCmd == win32.SW_SHOWNORMAL

    def __str__(self) -> str:
        return f"handle: {self.handle}, " \
               f"process_id: {self.process_id}, " \
               f"process_name: {self.process_name}, " \
               f"window_name: {self.window_name}, " \
               f"class_name: {self.class_name}"


class Element(ABC):
    @property
    @abstractmethod
    def driver(self) -> Driver:
        raise NotImplementedError

    @property
    @abstractmethod
    def rectangle(self) -> tuple[int, int, int, int]:
        raise NotImplementedError

    def screenshot(self, filename: str = None) -> Image:
        self.driver.set_foreground()
        time.sleep(0.06)
        return screenshot(self.rectangle, filename)

    def wait(self, predicate: Callable[[any], bool], timeout=None, interval=None):
        start = time.perf_counter()
        while not predicate(self):
            time_left = timeout - (time.perf_counter() - start)
            if time_left > 0:
                time.sleep(min(interval, time_left))
            else:
                err = TimeoutError("timed out")
                raise err
