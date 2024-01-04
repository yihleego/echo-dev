import os
import re
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

    def _matches(self, snapshot, rules, *filters: Callable[[any], bool], **criteria) -> bool:
        if len(filters) == 0 and len(criteria) == 0:
            return False

        def _do_expr(expr, fixed, value):
            if expr == "eq":
                return fixed == value
            if expr == "like":
                return fixed.find(value) >= 0
            if expr == "in":
                return fixed in value
            if expr == "in_like":
                for v in value:
                    if fixed.find(v) >= 0:
                        return True
                return False
            if expr == "regex":
                return re.match(value, fixed) is not None
            if expr == "gt":
                return fixed > value
            if expr == "gte":
                return fixed >= value
            if expr == "lt":
                return fixed < value
            if expr == "lte":
                return fixed <= value
            raise ValueError(f"unknown expression: {expr}")

        def _do_prop(obj, prop):
            if "." not in prop:
                return getattr(obj, prop)
            val = obj
            levels = prop.split(".")
            for level in levels:
                if not val:
                    return None
                val = getattr(val, level)
            return val

        if filters:
            for filter in filters:
                if not filter(snapshot):
                    return False
        if criteria:
            data = {}
            for key, (prop, exprs) in rules.items():
                for expr in exprs:
                    fullkey = key if expr == "eq" else key + "_" + expr
                    if fullkey in criteria:
                        data[fullkey] = (prop, expr)
                        break
            if len(criteria) != len(data):
                diff = criteria.keys() - data.keys()
                if len(diff) > 0:
                    raise Exception(f"Unsupported key(s): {', '.join(diff)}")
            for key, (prop, expr) in data.items():
                cri_val = criteria.get(key)
                if cri_val is None:
                    continue
                prop_val = _do_prop(snapshot, prop)
                if prop_val is None:
                    return False
                if not _do_expr(expr, prop_val, cri_val):
                    return False
        return True

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
