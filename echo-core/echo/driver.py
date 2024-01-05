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


import os
import time
from abc import ABC, abstractmethod
from typing import Callable

from PIL import Image, ImageGrab

from .utils import win32


class Element(ABC):

    @property
    @abstractmethod
    def handle(self) -> int:
        pass

    @property
    @abstractmethod
    def process_id(self) -> int:
        pass

    @property
    @abstractmethod
    def rectangle(self) -> tuple[int, int, int, int]:
        pass

    def wait(self, predicate: Callable[[any], bool], timeout=None, interval=None):
        start = time.perf_counter()
        while not predicate(self):
            time_left = timeout - (time.perf_counter() - start)
            if time_left > 0:
                time.sleep(min(interval, time_left))
            else:
                err = TimeoutError("timed out")
                raise err

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

    def screenshot(self, filename: str = None) -> Image:
        self.set_foreground()
        time.sleep(0.06)
        image = ImageGrab.grab(self.rectangle)
        dirname = os.path.dirname(filename)
        if filename:
            if not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True)
            image.save(filename)
        return filename


class Driver(ABC):
    pass
