import os
import time
from abc import ABC, abstractmethod

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

    def set_foreground(self) -> bool:
        self.show()
        return win32.set_foreground(self.handle, self.process_id)

    def move(self, x: int = None, y: int = None, width: int = None, height: int = None, repaint=True) -> bool:
        if x is None or y is None or width is None or height is None:
            rect = self.root.rectangle
            if x is None:
                x = rect[0]
            if y is None:
                y = rect[1]
            if width is None:
                width = rect[2] - rect[0]
            if height is None:
                height = rect[3] - rect[1]
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
